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

from keystone import assignment
from keystone.common import cass
from keystone import exception

from cassandra.cqlengine import columns
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.management import sync_table


class Role(assignment.RoleDriver):

    #@sql.handle_conflicts(conflict_type='role')
    def create_role(self, role_id, role):
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

    def _get_role(self, role_id):
        try:
            ref = RoleModel.get(id=role_id)
        except DoesNotExist:
            raise exception.RoleNotFound(role_id=role_id)
        return ref.to_dict()

    def get_role(self, role_id):
        return self._get_role(role_id)

    #@sql.handle_conflicts(conflict_type='role')
    def update_role(self, role_id, role):
        ref_dict = self._get_role(role_id)
        for key in role:
            ref_dict[key] = role[key]
        ref_id = ref_dict.pop('id')
        model_dict = RoleModel.get_model_dict(ref_dict)
        RoleModel.objects(id=ref_id).update(**model_dict)
        model_dict['id'] = ref_id
        return model_dict

    def delete_role(self, role_id):
        RoleModel.objects(id=role_id).delete()


class RoleModel(cass.ExtrasModel):
    id = columns.Text(primary_key=True, max_length=64)
    name = columns.Text(max_length=255, required=True)
    extra = columns.Text(default='')

cass.connect_to_cluster(cass.ips, cass.keyspace)

sync_table(RoleModel)

