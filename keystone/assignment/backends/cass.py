# Copyright 2012-13 OpenStack Foundation
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
from oslo_log import log
import six

from keystone import assignment as keystone_assignment
from keystone.common import cass
from keystone import exception
from keystone.i18n import _

from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine.query import BatchQuery
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.query import BatchType, DoesNotExist


CONF = cfg.CONF
LOG = log.getLogger(__name__)


class AssignmentType(object):
    USER_PROJECT = 'UserProject'
    GROUP_PROJECT = 'GroupProject'
    USER_DOMAIN = 'UserDomain'
    GROUP_DOMAIN = 'GroupDomain'

    @classmethod
    def calculate_type(cls, user_id, group_id, project_id, domain_id):
        if user_id:
            if project_id:
                return cls.USER_PROJECT
            if domain_id:
                return cls.USER_DOMAIN
        if group_id:
            if project_id:
                return cls.GROUP_PROJECT
            if domain_id:
                return cls.GROUP_DOMAIN
        # Invalid parameters combination
        raise exception.AssignmentTypeCalculationError(**locals())


class Assignment(keystone_assignment.Driver):

    def default_role_driver(self):
        return "keystone.assignment.role_backends.sql.Role"

    def default_resource_driver(self):
        return 'keystone.resource.backends.sql.Resource'

    def list_user_ids_for_project(self, tenant_id):

        # NOT checking distinctness
        refs = RoleAssignment.objects.filter(
                target_id=tenant_id)
        return [ref.actor_id for ref in refs if
                ref.type==AssignmentType.USER_PROJECT]

    def _get_metadata(self, user_id=None, tenant_id=None,
                      domain_id=None, group_id=None, session=None):
        ## TODO(henry-nash): This method represents the last vestiges of the old
        ## metadata concept in this driver.  Although we no longer need it here,
        ## since the Manager layer uses the metadata concept across all
        ## assignment drivers, we need to remove it from all of them in order to
        ## finally remove this method.
        def _calc_assignment_type():
            # Figure out the assignment type we're checking for from the args.
            if user_id:
                if tenant_id:
                    return AssignmentType.USER_PROJECT
                else:
                    return AssignmentType.USER_DOMAIN
            else:
                if tenant_id:
                    return AssignmentType.GROUP_PROJECT
                else:
                    return AssignmentType.GROUP_DOMAIN

        refs = RoleAssignment.objects.filter(
                type=_calc_assignment_type(),
                actor_id=(user_id or group_id),
                target_id=(tenant_id or domain_id))
        if not refs:
            raise exception.MetadataNotFound()

        metadata_ref = {}
        metadata_ref['roles'] = []
        for assignment in refs:
            role_ref = {}
            role_ref['id'] = assignment.role_id
            if assignment.inherited:
                role_ref['inherited_to'] = 'projects'
            metadata_ref['roles'].append(role_ref)

        return metadata_ref

    def create_grant(self, role_id, user_id=None, group_id=None,
                     domain_id=None, project_id=None,
                     inherited_to_projects=False):

        assignment_type = AssignmentType.calculate_type(
            user_id, group_id, project_id, domain_id)

        # NOTE(rushiagr): we're ignoring if a DB entry is present, and
        # overwriting it
        RoleAssignment(
                type=assignment_type,
                actor_id=(user_id or group_id),
                target_id=(project_id or domain_id),
                role_id=role_id,
                inherited=inherited_to_projects).save() # save() required?

    def list_grant_role_ids(self, user_id=None, group_id=None,
                            domain_id=None, project_id=None,
                            inherited_to_projects=False):
        refs_list = []
        for type in [AssignmentType.USER_PROJECT,
                AssignmentType.USER_DOMAIN,
                AssignmentType.GROUP_PROJECT,
                AssignmentType.GROUP_DOMAIN]:
            refs_list.append(RoleAssignment.objects.filter(
                    type=type,
                    actor_id=(user_id or group_id),
                    target_id=(project_id or domain_id),
                    #inherited=inherited_to_projects
                    ))

        role_list = []
        for refs in refs_list:
            for ref in refs:
                if ref.inherited == inherited_to_projects:
                    role_list.append(ref.role_id)
        return role_list

    def _build_grant_filter(self, role_id, user_id, group_id,
                            domain_id, project_id, inherited_to_projects):
        def _calc_assignment_type():
            # Figure out the assignment type we're checking for from the args.
            if user_id:
                if project_id:
                    return AssignmentType.USER_PROJECT
                else:
                    return AssignmentType.USER_DOMAIN
            elif group_id:
                if project_id:
                    return AssignmentType.GROUP_PROJECT
                else:
                    return AssignmentType.GROUP_DOMAIN
        refs = RoleAssignment.objects.filter(
                type=_calc_assignment_type(),
                actor_id=(user_id or group_id),
                target_id=(project_id or domain_id),
                role_id=role_id,
                inherited=inherited_to_projects)
        return refs

    def check_grant_role_id(self, role_id, user_id=None, group_id=None,
                            domain_id=None, project_id=None,
                            inherited_to_projects=False):
        refs = self._build_grant_filter(
                    role_id, user_id, group_id, domain_id, project_id,
                    inherited_to_projects)
        if len(refs) == 0:
            raise exception.RoleNotFound(role_id=role_id)

    def delete_grant(self, role_id, user_id=None, group_id=None,
                     domain_id=None, project_id=None,
                     inherited_to_projects=False):
        # TODO(rushiagr): move length checking also to _build_grant_filter, and
        # rename that method
        refs = self._build_grant_filter(
                    role_id, user_id, group_id, domain_id, project_id,
                    inherited_to_projects)
        if len(refs) == 0:
            raise exception.RoleNotFound(role_id=role_id)

        refs[0].delete()

    def _list_project_ids_for_actor(self, actors, hints, inherited,
                                    group_only=False):
        # TODO(henry-nash): Now that we have a single assignment table, we
        # should be able to honor the hints list that is provided.

        assignment_type = [AssignmentType.GROUP_PROJECT]
        if not group_only:
            assignment_type.append(AssignmentType.USER_PROJECT)


        # NOT checking distinctness
        refs = RoleAssignment.objects.filter(
                type__in=assignment_type,
                inherited=inherited,
                actor_id__in=actors)
        return [ref.target_id for ref in refs]


    def list_project_ids_for_user(self, user_id, group_ids, hints,
                                  inherited=False):
        actor_list = [user_id]
        if group_ids:
            actor_list = actor_list + group_ids

        return self._list_project_ids_for_actor(actor_list, hints, inherited)

    def list_domain_ids_for_user(self, user_id, group_ids, hints,
                                 inherited=False):
        # 'domain_ids is a dictionary, where keys are domain IDs, and values
        # are empty strings. Using dictionary for uniqueness
        domain_ids = {}

        if user_id:
            refs = RoleAssignment.objects.filter(
                    actor_id=user_id,
                    inherited=inherited,
                    type=AssignmentType.USER_DOMAIN)
            for ref in refs:
                domain_ids[ref.target_id] = ''

        if group_ids:
            refs = RoleAssignment.objects.filter(
                    actor_id__in=group_ids,
                    inherited=inherited,
                    type=AssignmentType.GROUP_DOMAIN)
            for ref in refs:
                domain_ids[ref.target_id] = ''

        return domain_ids.keys()

    def list_role_ids_for_groups_on_domain(self, group_ids, domain_id):
        if not group_ids:
            # If there's no groups then there will be no domain roles.
            return []

        # 'role_ids' is a dictionary, where keys are role IDs, and values
        # are empty strings. Using dictionary for uniqueness
        role_ids = {}

        refs = RoleAssignment.objects.filter(
                type=AssignmentType.GROUP_DOMAIN,
                target_id=domain_id,
                inherited=False,
                actor_id__in=group_ids)
        for ref in refs:
            domain_ids[ref.role_id] = ''

        return role_ids.keys()

    def list_role_ids_for_groups_on_project(
            self, group_ids, project_id, project_domain_id, project_parents):

        if not group_ids:
            # If there's no groups then there will be no project roles.
            return []

        # 'role_ids' is a dictionary, where keys are role IDs, and values
        # are empty strings. Using dictionary for uniqueness
        role_ids = {}

        # NOTE(rodrigods): First, we always include projects with
        # non-inherited assignments
        refs = RoleAssignment.objects.filter(
                target_id=project_id)
                #inherited=False)
        for ref in refs:
            if ref.type == AssignmentType.GROUP_PROJECT:
                role_ids[ref.role_id] = ''

        if CONF.os_inherit.enabled:
            # Inherited roles from domains
            refs = RoleAssignment.objects.filter(
                    #inherited=True, #TODO(rushiagr): sql has no 'True'!!
                    target_id=project_domain_id)
            for ref in refs:
                if ref.type == AssignmentType.GROUP_DOMAIN:
                    role_ids[ref.role_id] = ''

            # Inherited roles from projects
            if project_parents:
                refs = RoleAssignment.objects.filter(
                        #inherited=True, #TODO(rushiagr): sql has no 'True'!!
                        target_id__in=project_parents)
                for ref in refs:
                    if ref.type == AssignmentType.GROUP_PROJECT:
                        role_ids[ref.role_id] = ''
        return role_ids.keys()

    def list_project_ids_for_groups(self, group_ids, hints,
                                    inherited=False):
        return self._list_project_ids_for_actor(
            group_ids, hints, inherited, group_only=True)

    def list_domain_ids_for_groups(self, group_ids, inherited=False):
        if not group_ids:
            # If there's no groups then there will be no domains.
            return []

        # 'domain_ids' is a dictionary, where keys are domain IDs, and values
        # are empty strings. Using dictionary for uniqueness
        domain_ids = {}
        refs = RoleAssignment.objects.filter(
                type=AssignmentType.GROUP_DOMAIN,
                inherited=inherited,
                target_id__in=group_ids)
        for ref in refs:
            domain_ids[ref.target_id] = ''
        return domain_ids.keys()

    def add_role_to_user_and_project(self, user_id, tenant_id, role_id):
        # NOTE(rushiagr): we're doing a read, and then a write here, preserving
        # the case when the exception will be thrown. Another alternative would
        # be to just do a write, which will overwrite a previous value if it
        # existed, and this won't raise an exception
        #import pdb; pdb.set_trace()
        refs = RoleAssignment.objects.filter(
                type=AssignmentType.USER_PROJECT,
                actor_id=user_id)
        refs = [ref for ref in refs if ref.target_id == tenant_id and ref.role_id == role_id ]
        if len(refs) != 0:
            msg = ('User %s already has role %s in tenant %s'
                   % (user_id, role_id, tenant_id))
            raise exception.Conflict(type='role grant', details=msg)

        RoleAssignment.create(
            type=AssignmentType.USER_PROJECT,
            actor_id=user_id,
            target_id=tenant_id,
            role_id=role_id,
            inherited=False)

    def remove_role_from_user_and_project(self, user_id, tenant_id, role_id):
        role_found = False
        for type in [AssignmentType.USER_PROJECT,
                AssignmentType.USER_DOMAIN,
                AssignmentType.GROUP_PROJECT,
                AssignmentType.GROUP_DOMAIN]:
            refs = RoleAssignment.filter(type=type, actor_id=user_id)
            for ref in refs:
                if ref.target_id == tenant_id and ref.role_id == role_id:
                    role_found = True
                    ref.delete()

        if not role_found:
            raise exception.RoleNotFound(message=_(
                'Cannot remove role that has not been granted, %s') %
                role_id)

    def list_role_assignments(self):

        def denormalize_role(ref):
            assignment = {}
            if ref.type == AssignmentType.USER_PROJECT:
                assignment['user_id'] = ref.actor_id
                assignment['project_id'] = ref.target_id
            elif ref.type == AssignmentType.USER_DOMAIN:
                assignment['user_id'] = ref.actor_id
                assignment['domain_id'] = ref.target_id
            elif ref.type == AssignmentType.GROUP_PROJECT:
                assignment['group_id'] = ref.actor_id
                assignment['project_id'] = ref.target_id
            elif ref.type == AssignmentType.GROUP_DOMAIN:
                assignment['group_id'] = ref.actor_id
                assignment['domain_id'] = ref.target_id
            else:
                raise exception.Error(message=_(
                    'Unexpected assignment type encountered, %s') %
                    ref.type)
            assignment['role_id'] = ref.role_id
            if ref.inherited:
                assignment['inherited_to_projects'] = 'projects'
            return assignment

        refs = RoleAssignment.objects.all()
        return [denormalize_role(ref) for ref in refs]

    def delete_project_assignments(self, project_id):
        # NOTE(rushiagr): this throws DoesNotExist error, so add try..except
        # block temporarily
        try:
            ref = RoleAssignment.get(target_id=project_id)
            ref.delete()
        except DoesNotExist:
            pass

    def delete_role_assignments(self, role_id):
        # TODO: batch operation here
        refs = RoleAssignment.filter(role_id=role_id)
        for ref in refs:
            ref.delete()

    def delete_user_assignments(self, user_id):
        refs_list = []
        for type in [AssignmentType.USER_PROJECT,
                AssignmentType.USER_DOMAIN,
                AssignmentType.GROUP_PROJECT,
                AssignmentType.GROUP_DOMAIN]:
            refs_list.append(RoleAssignment.filter(type=type, actor_id=user_id))
        for refs in refs_list:
            for ref in refs:
                ref.delete()

    def delete_group_assignments(self, group_id):
        refs_list = []
        for type in [AssignmentType.USER_PROJECT,
                AssignmentType.USER_DOMAIN,
                AssignmentType.GROUP_PROJECT,
                AssignmentType.GROUP_DOMAIN]:
            refs_list.append(RoleAssignment.filter(type=type, actor_id=group_id))
        for refs in refs_list:
            for ref in refs:
                ref.delete()

class RoleAssignment(cass.ExtrasModel):
    __tablename__ = 'assignment'
    type = columns.Text(primary_key=True, partition_key=True, max_length=64)
    actor_id = columns.Text(primary_key=True, partition_key=True, max_length=64)
    target_id = columns.Text(primary_key=True, index=True, max_length=64)
    role_id = columns.Text(primary_key=True, index=True, max_length=64)
    inherited = columns.Boolean(default=False, required=True, index=True)

connection.setup(cass.ips, cass.keyspace)
sync_table(RoleAssignment)
