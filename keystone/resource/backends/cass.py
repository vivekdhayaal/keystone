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

from keystone.common import cass
from keystone import exception
from keystone import identity
from keystone.common import utils
from keystone.i18n import _
from keystone.i18n import _LE
from keystone import resource as keystone_resource

from keystone.common import sql
from keystone import clean

from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import BatchType, DoesNotExist

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class Domain(cass.ExtrasModel):
    __table_name__ = 'domain'
    id = columns.Text(primary_key=True, max_length=64)
    name = columns.Text(max_length=64) # IN SQL version length<64 IDK why.
    enabled = columns.Boolean(default=True)
    extra = columns.Text()

class DomainGSIName(cass.ExtrasModel):
    __table_name__ = 'domain_gsi_name'
    name = columns.Text(primary_key=True, max_length=64)
    domain_id = columns.Text(max_length=64)

class Project(cass.ExtrasModel):
    __table_name__ = 'project'
    id = columns.Text(primary_key=True, max_length=64)
    name = columns.Text(max_length=64) # IN SQL version length<64 IDK why.
    domain_id = columns.Text(max_length=255, index=True)
    description = columns.Text()
    enabled = columns.Boolean()
    extra = columns.Text()
    parent_id = columns.Text(max_length=255)
    name = columns.Text(max_length=255)

class ProjectGSINameDomainId(cass.ExtrasModel):
    __table_name__ = 'project_gsi_name_domain_id'
    name = columns.Text(primary_key=True, partition_key=True,  max_length=64)
    domain_id = columns.Text(primary_key=True, partition_key=True, max_length=64)
    project_id = columns.Text(max_length=64)

#cass.connect_to_cluster()

#sync_table(Domain)
#sync_table(DomainGSIName)
#sync_table(Project)
#sync_table(ProjectGSINameDomainId)

class Resource(keystone_resource.Driver):

    def default_assignment_driver(self):
        return 'sql'

    def _get_project(self, project_id):
        try:
            return Project.get(id=project_id)
        except DoesNotExist:
            raise exception.ProjectNotFound(project_id=project_id)


    def get_project(self, tenant_id):
        return self._get_project(tenant_id).to_dict()

    def get_project_by_name(self, tenant_name, domain_id):
        try:
            project_gsi_ref = ProjectGSINameDomainId.get(name=tenant_name,
                    domain_id=domain_id)
            project_ref = Project.get(id=project_gsi_ref.project_id)
        except DoesNotExist:
            raise exception.ProjectNotFound(project_id=tenant_name)


        return project_ref.to_dict()

    @cass.truncated
    def list_projects(self, hints):
        # NOTE(rushiagr): All the time we're only talking about filtering
        # based on hints if the filter key is a secondary index or a GSI. BUT
        # what if it's the primary key itself of the table? E.g., here in
        # list_projects, say the filter is 'id=<a project id>'?. It seems
        # quite likely that this might happen, and we should implement this.

        # TODO(rushiagr): filter hints if the filter is the primary key
        # TODO(rushiagr): filter hints based on GSI

        x_cols = cass.get_exact_comparison_columns(hints)
        if len(x_cols) == 1 and cass.is_secondary_idx_on_col(Project, x_cols[0]):
            filt = hints.filters[0]
            kv_dict = {filt['name']: filt['value']}
            refs = Project.objects.filter(**kv_dict)
        else:
            refs = Project.objects.all()
        return [ref.to_dict() for ref in refs]


    def list_projects_from_ids(self, ids):
        if not ids:
            return []
        else:
            refs = Project.objects.filter(id__in=ids)
            return [ref.to_dict() for ref in refs]

    def list_project_ids_from_domain_ids(self, domain_ids):
        if not domain_ids:
            return []
        else:
            refs_list = []
            for domain_id in domain_ids:
                refs = Project.objects.filter(domain_id=domain_id)
                refs_list.append(refs)
            return_list = []
            for refs in refs_list:
                return_list.extend([ref.id for ref in refs])

    def list_projects_in_domain(self, domain_id):
        refs = Project.objects.filter(domain_id=domain_id)
        return [ref.to_dict() for ref in refs]

    def _get_children(self, project_ids):
        pass

    def list_projects_in_subtree(self, project_id):
        raise exception.NotImplemented()

    def list_project_parents(self, project_id):
        raise exception.NotImplemented()

    def is_leaf_project(self, project_id):
        return True
        #raise NotImplementedError()

    # CRUD
    @cass.handle_conflicts(conflict_type='project')
    def create_project(self, tenant_id, tenant):
        try:
            ref = Project.get(id=tenant['id'])
            raise exception.Conflict(type='object',
                    details=_('Duplicate Entry'))
        except DoesNotExist:
            pass

        try:
            gsi_ref = ProjectGSINameDomainId.get(name=tenant['name'], domain_id=tenant['domain_id'])
            raise exception.Conflict(type='object',
                    details=_('Duplicate Entry'))
        except DoesNotExist:
            pass

        tenant['name'] = clean.project_name(tenant['name'])
        tenant['id'] = tenant_id

        project_create_dict = Project.get_model_dict(tenant)
        ref = Project.create(**project_create_dict)
        gsi_create_dict = {
                'name': tenant['name'],
                'domain_id': tenant['domain_id'],
                'project_id': tenant_id,
                }
        gsi_ref = ProjectGSINameDomainId.create(**gsi_create_dict)
        return ref.to_dict()

    #@sql.handle_conflicts(conflict_type='project')
    def update_project(self, tenant_id, tenant):
        if 'name' in tenant:
            tenant['name'] = clean.project_name(tenant['name'])

        tenant_ref = self._get_project(tenant_id)
        old_project_dict = tenant_ref.to_dict()

        if (old_project_dict['name'] != tenant['name'] or
                old_project_dict['domain_id'] != tenant['domain_id']):
            exception.ForbiddenAction(message='project name or domain_id cannot be updated')

        # NOTE(rushiagr): Following commented code is left here
        # intentionally. This is because when we would want to write tests
        # to pass tempest, we might have to write update functionality too
        # even though it is not very efficient and is racy with distributed
        # databases
        #gsi_updated = False
        #if (old_project_dict['name'] != tenant['name'] or
        #        old_project_dict['domain_id'] != tenant['domain_id']):
        #    gsi_updated = True

        for key in tenant:
            old_project_dict[key] = tenant[key]
        new_project_dict = Project.get_model_dict(old_project_dict)

        # Just creating another entry with same ID will override existing one
        ref = Project.create(**new_project_dict)

        #if gsi_updated:
        #    gsi_dict = {'name': new_project_dict['name'],
        #        'domain_id': new_project_dict['domain_id'],
        #        'project_id': new_project_dict['id']
        #        }
        #    new_gsi_dict = ProjectGSINameDomainId.get_model_dict(
        #        gsi_dict, extras_table=False)
        #    ProjectGSINameDomainId.create(**new_gsi_dict)

        return ref.to_dict()


    #@sql.handle_conflicts(conflict_type='project')
    def delete_project(self, tenant_id):
        try:
            ref = Project.get(id=tenant_id)
            Project(id=tenant_id).delete()
            ProjectGSINameDomainId(name=ref.name, domain_id=ref.domain_id).delete()
        except DoesNotExist:
            pass



    # domain crud

    #@sql.handle_conflicts(conflict_type='domain')
    def create_domain(self, domain_id, domain):
        domain_create_dic = Domain.get_model_dict(domain)
        ref = Domain.create(**domain_create_dic)

        gsi_create_dict = {'name': domain_create_dic['name'],
                'domain_id': domain_create_dic['id']}
        gsi_ref = DomainGSIName.create(**gsi_create_dict)

        return ref.to_dict()

    #@sql.truncated
    def list_domains(self, hints):
        # NOTE(rushiagr): No secondary index on Domain table, so skip hints!
        refs = Domain.objects.all()
        return [ref.to_dict() for ref in refs]

    def list_domains_from_ids(self, ids):
        if not ids:
            return []
        else:
            refs = Domain.objects.filter(id__in=ids)
            return [ref.to_dict() for ref in refs]

    def _get_domain(self, domain_id):
        try:
            return Domain.get(id=domain_id)
        except DoesNotExist:
            raise exception.DomainNotFound(domain_id=domain_id)

    def get_domain(self, domain_id):
        return self._get_domain(domain_id).to_dict()

    def get_domain_by_name(self, domain_name):
        try:
            gsi_ref = DomainGSIName.get(name=domain_name)
            return Domain.get(id=gsi_ref.domain_id).to_dict()
        except DoesNotExist:
            raise exception.DomainNotFound(domain_id=domain_name)

    @sql.handle_conflicts(conflict_type='domain')
    def update_domain(self, domain_id, domain):
        old_dict = self._get_domain(domain_id).to_dict()

        # See if GSI needs to be updated
        # TODO(rushiagr): general function to find out if GSI is updated

        if old_dict['name'] != domain['name']:
            exception.ForbiddenAction(message='domain name cannot be updated')

        # NOTE(rushiagr): Following commented code is left here
        # intentionally. This is because when we would want to write tests
        # to pass tempest, we might have to write update functionality too
        # even though it is not very efficient and is racy with distributed
        # databases
        #gsi_updated = False
        #if old_dict['name'] != domain['name']:
        #    gsi_updated = True

        for key in domain:
            old_dict[key] = domain[key]

        new_dict = Domain.get_model_dict(old_dict)
        ref = Domain.create(**new_dict)

        #if gsi_updated:
        #    gsi_dict = {'name': new_dict['name'],
        #            'domain_id': domain_id}
        #    new_gsi_dict = DomainGSIName.get_model_dict(
        #            gsi_dict, extras_table=False)
        #    DomainGSIName.create(**new_gsi_dict)

        return ref.to_dict()

    def delete_domain(self, domain_id):
        try:
            ref = Domain.get(id=domain_id)
            Domain(id=domain_id).delete()
            DomainGSIName(name=ref.name).delete()
        except DoesNotExist:
            pass
