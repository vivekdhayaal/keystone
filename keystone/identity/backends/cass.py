# Copyright 2012 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg

from keystone.common import cass
from keystone import exception
from keystone import identity
from keystone.common import utils
from keystone.i18n import _

from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import BatchType, DoesNotExist

CONF = cfg.CONF


class User(cass.ExtrasModel):
    __table_name__ = 'user'
    id = columns.Text(primary_key=True, max_length=64)
    name = columns.Text(max_length=255)
    domain_id = columns.Text(max_length=64, index=True)
    password = columns.Text(max_length=128)
    enabled = columns.Boolean()
    extra = columns.Text()
    default_project_id = columns.Text(max_length=64)

## GSI of 'user' table, with domain_id as the partition key
## and user_id as the clustering column. This table is for query
## 'select all users from a particular domain'
#class GSIUserDomainIdUserId(Model):
#    __table_name__ = 'gsi_user0domain_id0id0pk0id0user_id0cc'
#    # The table name means the table is a GSI on 'user' table, where
#    # domain_id column of user table is 'id' of this table which is a
#    # partition key, and 'id' column of user table is user_id of this table
#    # which is a clustering column of the primary key.
#    # TODO(rushiagr): move this comment to a common place when this
#    # convention needs to be followed while creating new GSIs
#    id = columns.Text(primary_key=True, max_length=64)
#    user_id = columns.Text(primary_key=True, max_length=64)

class DomainIdUserNameToUserId(cass.ExtrasModel):
    __table_name__ = 'domain_id_user_name_to_user_id'
    domain_id = columns.Text(primary_key=True, max_length=64)
    name = columns.Text(primary_key=True, max_length=255)
    user_id = columns.Text(max_length=64)

class Group(cass.ExtrasModel):
    __table_name__ = 'group'
    id = columns.Text(primary_key=True, max_length=64)
    name = columns.Text(max_length=64)
    domain_id = columns.Text(max_length=64, index=True)
    description = columns.Text()
    extra = columns.Text()

class DomainIdGroupNameToGroupId(cass.ExtrasModel):
    __table_name__ = 'domain_id_group_name_to_group_id'
    domain_id = columns.Text(primary_key=True, max_length=64)
    name = columns.Text(primary_key=True, max_length=64)
    group_id = columns.Text(max_length=64)

class UserGroups(cass.ExtrasModel):
    __table_name__ = 'user_groups'
    user_id = columns.Text(primary_key=True, max_length=64)
    group_id = columns.Text(primary_key=True, clustering_order="DESC", max_length=64)

class GroupMembership(cass.ExtrasModel):
    __table_name__ = 'group_users'
    group_id = columns.Text(primary_key=True, max_length=64)
    user_id = columns.Text(primary_key=True, clustering_order="DESC", max_length=64)

connection.setup(cass.ips, cass.keyspace)

sync_table(User)
sync_table(DomainIdUserNameToUserId)
sync_table(Group)
sync_table(DomainIdGroupNameToGroupId)
sync_table(UserGroups)
sync_table(GroupMembership)

class Identity(identity.Driver):
    # NOTE(henry-nash): Override the __init__() method so as to take a
    # config parameter to enable sql to be used as a domain-specific driver.
    def __init__(self, conf=None):
        super(Identity, self).__init__()

    def default_assignment_driver(self):
        return "keystone.assignment.backends.sql.Assignment"

    @property
    def is_sql(self):
        return False

    def _check_password(self, password, user_ref):
        """Check the specified password against the data store.

        Note that we'll pass in the entire user_ref in case the subclass
        needs things like user_ref.get('name')
        For further justification, please see the follow up suggestion at
        https://blueprints.launchpad.net/keystone/+spec/sql-identiy-pam

        """
        return utils.check_password(password, user_ref.password)

    # Identity interface
    def authenticate(self, user_id, password):
        user_ref = None
        try:
            user_ref = self._get_user(user_id)
        except exception.UserNotFound:
            raise AssertionError(_('Invalid user / password'))
        if not self._check_password(password, user_ref):
            raise AssertionError(_('Invalid user / password'))
        return identity.filter_user(user_ref.to_dict())

    # user crud

    def create_user(self, user_id, user):
        mapping_dict = user
        mapping_dict['user_id'] = user['id']
        mapping_ref = DomainIdUserNameToUserId.get_model_dict(mapping_dict,
                extras_table=False)
        DomainIdUserNameToUserId.create(**mapping_ref)

        user = utils.hash_user_password(user)
        user_model_dict = User.get_model_dict(user)
        user_ref = User.create(**user_model_dict)
        user_dict = user_ref.to_dict()
        return identity.filter_user(user_dict)


    @cass.truncated
    def list_users(self, hints):
        # @TODO: Implement complete hints!
        x_cols = cass.get_exact_comparison_columns(hints)
        if len(x_cols) == 1 and cass.is_secondary_idx_on_col(User, x_cols[0]):
            # We're here means there is exactly one filter in hints, and that
            # filter is an exact filter, and that for the attribute of filter,
            # there is a secondary index on that column
            filt = hints.filters[0]
            kv_dict = {filt['name']: filt['value']}
            user_refs = User.objects.filter(**kv_dict)
        else:
            user_refs = User.objects.all()

        return [identity.filter_user(x.to_dict()) for x in user_refs]

    def _get_user(self, user_id):
        result = None
        try:
            return User.get(id=user_id)
        except DoesNotExist:
            raise exception.UserNotFound(user_id=user_id)

    def get_user(self, user_id):
        user_dict = self._get_user(user_id).to_dict()
        return identity.filter_user(user_dict)

    def get_user_by_name(self, user_name, domain_id):
        results = DomainIdUserNameToUserId.objects.filter(domain_id=domain_id, name=user_name)
        uuid_ref = results.first()
        if uuid_ref is None:
            raise exception.UserNotFound(user_id=user_name)
        user_id = uuid_ref.user_id
        user_ref = User.objects.filter(id=user_id).first()
        if user_ref is None:
            raise exception.UserNotFound(user_id=user_name)
        return identity.filter_user(user_ref.to_dict())

    def update_user(self, user_id, user):

        user_ref = self._get_user(user_id)
        if 'name' in user and user_ref.name != user['name']:
            raise exception.ForbiddenAction(message='name cannot be updated')
        if 'domain_id' in user and user_ref.domain_id != user['domain_id']:
            raise exception.ForbiddenAction(message='domain cannot be updated')

        user = utils.hash_user_password(user)
        user_dict = User.get_model_dict(user)
        User.objects(id=user_id).update(**user_dict)
        user_ref = self._get_user(user_id)
        return identity.filter_user(user_ref.to_dict())

    def add_user_to_group(self, user_id, group_id):
        self.get_group(group_id)
        self.get_user(user_id)
        try:
            GroupMembership.get(group_id=group_id, user_id=user_id)
        except DoesNotExist:
            GroupMembership.create(group_id=group_id, user_id=user_id)
        try:
            UserGroups.get(user_id=user_id, group_id=group_id)
        except DoesNotExist:
            UserGroups.create(user_id=user_id, group_id=group_id)

    def check_user_in_group(self, user_id, group_id):
        self.get_group(group_id)
        self.get_user(user_id)
        try:
            GroupMembership.get(group_id=group_id, user_id=user_id)
        except DoesNotExist:
            raise exception.NotFound(_("User '%(user_id)s' not found in"
                                       " group '%(group_id)s'") %
                                      {'user_id': user_id,
                                      'group_id': group_id})


    def remove_user_from_group(self, user_id, group_id):
        # We don't check if user or group are still valid and let the remove
        # be tried anyway - in case this is some kind of clean-up operation
        membership_ref = None
        try:
            membership_ref = GroupMembership.get(group_id=group_id, user_id=user_id)
            membership_ref.delete()
        except DoesNotExist:
            raise exception.NotFound(_("User '%(user_id)s' not found in"
                                       " group '%(group_id)s'") %
                                      {'user_id': user_id,
                                      'group_id': group_id})

        try:
            membership_ref = UserGroups.get(user_id=user_id, group_id=group_id)
            membership_ref.delete()
        except DoesNotExist:
            raise exception.NotFound(_("User '%(user_id)s' not found in"
                                       " group '%(group_id)s'") %
                                      {'user_id': user_id,
                                      'group_id': group_id})

    def list_groups_for_user(self, user_id, hints):
        # TODO(rushiagr) use the hints
        results = UserGroups.objects.filter(user_id=user_id)
        groups = []
        for result in results:
            gid = result.group_id
            gid_ref = Group.get(id=gid)
            groups.append(gid_ref.to_dict())

        return groups

    def list_users_in_group(self, group_id, hints):
        results = GroupMembership.objects.filter(group_id=group_id)
        users = []
        for result in results:
            uid = result.user_id
            uid_ref = User.get(id=uid)
            users.append(identity.filter_user(uid_ref.to_dict()))

        return users

    def delete_user(self, user_id):
        user_ref = self._get_user(user_id)
        User(id=user_id).delete()
        DomainIdUserNameToUserId(
                domain_id=user_ref.domain_id,
                name=user_ref.name).delete()

    # group crud

    #@sql.handle_conflicts(conflict_type='group')
    def create_group(self, group_id, group):
        group_create_dict = Group.get_model_dict(group)
        # TODO: check  if 'group' var has 'id', else take from group_id
        ref = Group.create(**group_create_dict)

        mapping_create_dict = {
                'domain_id': group['domain_id'],
                'name': group['name'],
                'group_id': group_id,
        }
        DomainIdGroupNameToGroupId.create(**mapping_create_dict)

        return ref.to_dict()

    @cass.truncated
    def list_groups(self, hints):
        # TODO(rushiagr): implement complete hints!
        x_cols = cass.get_exact_comparison_columns(hints)
        if len(x_cols) == 1 and cass.is_secondary_idx_on_col(Group, x_cols[0]):
            # We're here means there is exactly one filter in hints, and that
            # filter is an exact filter, and that for the attribute of filter,
            # there is a secondary index on that column
            filt = hints.filters[0]
            kv_dict = {filt['name']: filt['value']}
            refs = Group.objects.filter(**kv_dict)
        else:
            refs = Group.objects.all()

        return [ref.to_dict() for ref in refs]

    def _get_group(self, group_id):
        try:
            ref = Group.get(id=group_id)
        except DoesNotExist:
            raise exception.GroupNotFound(group_id=group_id)
        return ref

    def get_group(self, group_id):
        return self._get_group(group_id).to_dict()

    def get_group_by_name(self, group_name, domain_id):
        try:
            mapping_ref = DomainIdGroupNameToGroupId.get(domain_id=domain_id,
                name=group_name)
            group_ref = Group.get(mapping_ref.group_id)
            return group_ref.to_dict()
        except DoesNotExist:
            raise exception.GroupNotFound(group_id=group_name)

    #@sql.handle_conflicts(conflict_type='group')
    def update_group(self, group_id, group):
        group_ref = self._get_group(group_id)
        if 'name' in group and group_ref.name != group['name']:
            raise exception.ForbiddenAction(message='Name cannot be updated')
        if 'domain_id' in group and group_ref.domain_id != group['domain_id']:
            raise exception.ForbiddenAction(message='Domain cannot be updated')

        updated_dict = Group.get_model_dict(group)
        Group.objects(id=group_id).update(**updated_dict)
        group_ref = self._get_group(group_id)
        return group_ref.to_dict()

    def delete_group(self, group_id):
        group_ref = self._get_group(group_id)
        Group(id=group_id).delete()
        DomainIdGroupNameToGroupId(
                domain_id=group_ref.domain_id,
                name=group_ref.name).delete()
