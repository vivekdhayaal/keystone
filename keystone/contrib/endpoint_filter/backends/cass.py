# Copyright 2013 OpenStack Foundation
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
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import BatchType, DoesNotExist, MultipleObjectsReturned, BatchType, BatchQuery

import itertools

import six

from keystone import catalog
from keystone.catalog import core

CONF = cfg.CONF


class ProjectEndpoint(cass.ExtrasModel):
    """Project-endpoint relationship table.

    project_id is partition key, endpoint_id is clustering column"""
    __table_name__ = 'project_endpoint'
    project_id = columns.Text(primary_key=True, max_length=64)
    endpoint_id = columns.Text(primary_key=True, max_length=64)


class EndpointProject(cass.ExtrasModel):
    """Project-endpoint relationship table.

    Endpoint ID is the Partition key, Project ID is the clustering column."""
    __table_name__ = 'project_endpoint'
    endpoint_id = columns.Text(primary_key=True, max_length=64)
    project_id = columns.Text(primary_key=True, max_length=64)


class EndpointGroup(cass.ExtrasModel):
    """Endpoint Groups table."""
    __table_name__ = 'endpoint_group'
    id = columns.Text(primary_key=True, max_length=64)
    name = columns.Text(max_length=255)
    description = columns.Text()
    name = columns.Text()


class EndpointGroupProject(cass.ExtrasModel):
    """Project to Endpoint group relationship table."""
    __table_name__ = 'project_endpoint_group'
    endpoint_group_id = columns.Text(primary_key=True, max_length=64)
    project_id = columns.Text(primary_key=True, max_length=64)


class ProjectEndpointGroup(cass.ExtrasModel):
    """Project to Endpoint group relationship table."""
    __table_name__ = 'project_endpoint_group'
    project_id = columns.Text(primary_key=True, max_length=64)
    endpoint_group_id = columns.Text(primary_key=True, max_length=64)

cass.connect_to_cluster(cass.ips, cass.keyspace)

sync_table(ProjectEndpoint)
sync_table(EndpointProject)
sync_table(EndpointGroup)
sync_table(ProjectEndpointGroup)
sync_table(EndpointGroupProject)


class EndpointFilter(object):

    def add_endpoint_to_project(self, endpoint_id, project_id):

        # NOTE(rushiagr): we're assuming that if there is an entry
        # in ProjectEndpoint, an entry is present in EndpointProject. This
        # might not be true in some failure scenarios, and we might
        # need to check for it
        try:
            ref = ProjectEndpoint.get(endpoint_id=endpoint_id,
                    project_id=project_id)
            raise exception.Conflict(conflict_type='project_endpoint')
        except DoesNotExist:
            ProjectEndpoint.create(endpoint_id=endpoint_id,
                    project_id=project_id)
            EndpointProject.create(endpoint_id=endpoint_id,
                    project_id=project_id)

    def _get_project_endpoint_ref(self, endpoint_id, project_id):
        try:
            ref = ProjectEndpoint.get(endpoint_id=endpoint_id,
                    project_id=project_id)
            return ref
        except DoesNotExist:
            msg = _('Endpoint %(endpoint_id)s not found in project '
                    '%(project_id)s') % {'endpoint_id': endpoint_id,
                                         'project_id': project_id}
            raise exception.NotFound(msg)

    def check_endpoint_in_project(self, endpoint_id, project_id):
        self._get_project_endpoint_ref(endpoint_id, project_id)

    def remove_endpoint_from_project(self, endpoint_id, project_id):
        endpoint_filter_ref = self._get_project_endpoint_ref(
            endpoint_id, project_id)
        endpoint_filter_ref.delete()

    def list_endpoints_for_project(self, project_id):
        refs = ProjectEndpoint.objects.filter_by(project_id=project_id)
        return [ref.to_dict() for ref in refs]

    def list_projects_for_endpoint(self, endpoint_id):
        refs = EndpointProject.objects.filter_by(endpoint_id=endpoint_id)
        return [ref.to_dict() for ref in refs]

    def delete_association_by_endpoint(self, endpoint_id):
        refs = EndpointProject.objects.filter(endpoint_id=endpoint_id)
        with BatchQuery(batch_type=BatchType.Unlogged) as b:
            for ref in refs:
                ProjectEndpoint(project_id=ref.project_id,
                        endpoint_id=endpoint_id).delete()
                ref.batch(b).delete()

    def delete_association_by_project(self, project_id):
        refs = ProjectEndpoint.objects.filter(project_id=project_id)
        with BatchQuery(batch_type=BatchType.Unlogged) as b:
            for ref in refs:
                EndpointProject(endpoint_id=ref.endpoint_id,
                        project_id=project_id).delete()
                ref.batch(b).delete()

    def create_endpoint_group(self, endpoint_group_id, endpoint_group):
        create_dict = EndpointGroup.get_model_dict(endpoint_group)
        create_dict['id'] = endpoint_group_id
        ref = EndpointGroup.create(**create_dict)
        return ref.to_dict()

    def _get_endpoint_group(self, endpoint_group_id):
        try:
            ref = EndpointGroup.get(id=endpoint_group_ref)
            return ref
        except DoesNotExist:
            raise exception.EndpointGroupNotFound(
                    endpoint_group_id=endpoint_group_id)

    def get_endpoint_group(self, endpoint_group_id):
        endpoint_group_ref = self._get_endpoint_group(endpoint_group_id)
        return endpoint_group_ref.to_dict()


    def update_endpoint_group(self, endpoint_group_id, endpoint_group):
        create_dict = EndpointGroup.get_model_dict(endpoint_group)
        create_dict['id'] = endpoint_group_id
        ref = EndpointGroup.create(**create_dict)
        return ref.to_dict()

    def delete_endpoint_group(self, endpoint_group_id):

        # NOTE(rushiagr): First delete endpoint group associations with
        # projects, and then delete endpoint group.
        refs = ProjectEndpointGroup.objects.filter(
            endpoint_group_id=endpoint_group_id)
        with BatchQuery(batch_type=BatchType.Unlogged) as b:
            for ref in refs:
                EndpointGroupProject(project_id=ref.project_id,
                        endpoint_group_id=endpoint_group_id)
                ref.batch(b).delete()
            EndpointGroup(id=endpoint_group_id).batch(b).delete()

    def get_endpoint_group_in_project(self, endpoint_group_id, project_id):
        ref = self._get_endpoint_group_in_project(endpoint_group_id,
                                                  project_id)
        return ref.to_dict()

    def add_endpoint_group_to_project(self, endpoint_group_id, project_id):
        try:
            ref = ProjectEndpointGroup.get(
                    endpoint_group_id=endpoint_group_id,
                    project_id=project_id)
        except DoesNotExist:
            raise exception.Conflict(conflict_type='project_endpoint_group')
        with BatchQuery(batch_type=BatchType.Unlogged) as b:
            EndpointGroupProject.batch(b).create(
                    endpoint_group_id=endpoint_group_id,
                    project_id=project_id)
            ProjectEndpointGroup.batch(b).create(
                    endpoint_group_id=endpoint_group_id,
                    project_id=project_id)

    def _get_endpoint_group_in_project(self,
                                       endpoint_group_id, project_id):
        try:
            ref = ProjectEndpointGroup.get(
                    endpoint_group_id=endpoint_group_id,
                    project_id=project_id)
        except DoesNotExist:
            msg = _('Endpoint Group Project Association not found')
            raise exception.NotFound(msg)
        return ref


    def list_endpoint_groups(self):
        refs = EndpointGroup.objects.all()
        return [ref.to_dict() for ref in refs]

    def list_endpoint_groups_for_project(self, project_id):
        refs = EndpointGroupProject.objects.filter(project_id=project_id)
        return [ref.to_dict() for ref in refs]

    def remove_endpoint_group_from_project(self, endpoint_group_id,
                                           project_id):
        with BatchQuery(batch_type=BatchType.Unlogged) as b:
            EndpointGroupProject(endpoint_group_id=endpoint_group_id,
                    project_id=project_id).batch(b).delete()
            ProjectEndpointGroup(endpoint_group_id=endpoint_group_id,
                    project_id=project_id).batch(b).delete()


    def list_projects_associated_with_endpoint_group(self, endpoint_group_id):
        refs = ProjectEndpointGroup.objects.filter(
                endpoint_group_id=endpoint_group_id)
        return [ref.to_dict() for ref in refs]

    def _delete_endpoint_group_association_by_endpoint_group(
            self, endpoint_group_id):
        # NOTE(rushiagr): not used
        pass

    def delete_endpoint_group_association_by_project(self, project_id):
        refs = EndpointGroupProject.objects.filter(project_id=project_id)
        with BatchQuery(batch_type=BatchType.Unlogged) as b:
            for ref in refs:
                ProjectEndpointGroup(project_id=project_id,
                    endpoint_group_id=refs.endpoint_group_id).batch(b).delete()
                ref.batch(b).delete()
