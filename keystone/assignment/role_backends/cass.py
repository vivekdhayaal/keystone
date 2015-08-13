# Copyright 2015 Reliance Jio Infocomm Ltd.
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

from oslo_log import log

from keystone import assignment
from keystone.common import cass
from keystone import exception

from cassandra.cqlengine import columns
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.management import sync_table

LOG = log.getLogger(__name__)

class Role(assignment.RoleDriver):

    def create_role(self, role_id, role):
        try:
            RoleModel.get(id=role_id)
            # we are here means, a role of same id already exists
            # so raise exception
            # LOG the exception for debug purposes
            conflict_type = 'role'
            details = 'duplicate entry'
            _conflict_msg = 'Conflict %(conflict_type)s: %(details)s'
            LOG.debug(_conflict_msg, {'conflict_type': conflict_type,
                                      'details': details})
            raise exception.Conflict(type=conflict_type,
                                     details=_(details))
        except DoesNotExist:
            create_dict = RoleModel.get_model_dict(role)
            ref = RoleModel.create(**create_dict)
            return ref.to_dict()

    @cass.truncated
    def list_roles(self, hints):
        #FIXME: handle hints
        #refs = sql.filter_limit_query(RoleTable, query, hints)
        refs = RoleModel.objects.all()
        return [ref.to_dict() for ref in refs]

    def list_roles_from_ids(self, ids):
        if not ids:
            return []
        else:
            role_refs = RoleModel.objects.filter(id__in=ids)
            return [role_ref.to_dict() for role_ref in role_refs]

    def get_role(self, role_id):
        try:
            ref = RoleModel.get(id=role_id)
        except DoesNotExist:
            raise exception.RoleNotFound(role_id=role_id)
        return ref.to_dict()

    #@sql.handle_conflicts(conflict_type='role')
    #Vivek: there doesn't seem to a case when an update would result in a
    #conflict. So, ignoring the decorator for now.
    def update_role(self, role_id, role):
        #primary key update not permitted
        if 'id' in role:
            del role['id']
        model_dict = RoleModel.get_model_dict(role)
        RoleModel.objects(id=role_id).update(**model_dict)
        model_dict['id'] = role_id
        return model_dict

    def delete_role(self, role_id):
        RoleModel.objects(id=role_id).delete()


class RoleModel(cass.ExtrasModel):
    id = columns.Text(primary_key=True, max_length=64)
    name = columns.Text(max_length=255, required=True)
    extra = columns.Text(default='')

#cass.connect_to_cluster()

#sync_table(RoleModel)

