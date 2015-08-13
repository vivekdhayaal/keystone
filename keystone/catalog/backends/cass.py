# Copyright 2012 OpenStack Foundation
# Copyright 2012 Canonical Ltd.
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


class Region(cass.ExtrasModel):
    __table_name__ = 'region'
    id = columns.Text(primary_key=True, max_length=255)
    description = columns.Text(max_length=255)
    # NOTE(rushiagr): Keeping the column here, even though we're not using it
    # so as to avoid any failures, higher up. Even if I remove it, I think
    # our extras logic will handle it and put this attribute in extras column
    parent_region_id = columns.Text(max_length=255)
    extra = columns.Text()


class Service(cass.ExtrasModel):
    __table_name__ = 'service'
    id = columns.Text(primary_key=True, max_length=64)
    type = columns.Text(max_length=255)
    enabled = columns.Boolean(default=True, index=True)
    extra = columns.Text()


class Endpoint(cass.ExtrasModel):
    __table_name__ = 'endpoint'
    id = columns.Text(primary_key=True, max_length=64)
    legacy_endpoint_id = columns.Text(max_length=64)
    interface = columns.Text(max_length=8)
    region_id = columns.Text(max_length=255, index=True)
    #region_id = sql.Column(sql.String(255),
    #                       sql.ForeignKey('region.id',
    #                                      ondelete='RESTRICT'),
    # NOTE(rushiagr): make sure we handle ondelete restrict in our code
    #                       nullable=True,
    #                       default=None)
    service_id = columns.Text(max_length=64, index=True)
    url = columns.Text()
    enabled = columns.Boolean(default=True, index=True)
    extra = columns.Text()

#cass.connect_to_cluster()

#sync_table(Region)
#sync_table(Endpoint)
#sync_table(Service)




class Catalog(catalog.Driver):
    # Regions
    def list_regions(self, hints):
        # Ignore hints for now
        #session = sql.get_session()
        #regions = session.query(Region)
        #regions = sql.filter_limit_query(Region, regions, hints)
        #return [s.to_dict() for s in list(regions)]
        refs = Region.objects.all()
        return [ref.to_dict() for ref in refs]

    def _get_region(self, region_id):
        #ref = session.query(Region).get(region_id)
        #if not ref:
        #    raise exception.RegionNotFound(region_id=region_id)
        #return ref
        try:
            ref = Region.get(id=region_id)
            return ref
        except DoesNotExist:
            raise exception.RegionNotFound(region_id=region_id)

    def _delete_child_regions(self, session, region_id, root_region_id):
        #"""Delete all child regions.

        #Recursively delete any region that has the supplied region
        #as its parent.
        #"""
        #children = session.query(Region).filter_by(parent_region_id=region_id)
        #for child in children:
        #    if child.id == root_region_id:
        #        # Hit a circular region hierarchy
        #        return
        #    self._delete_child_regions(session, child.id, root_region_id)
        #    session.delete(child)
        raise exception.NotImplemented()

    def _check_parent_region(self, session, region_ref):
        """Raise a NotFound if the parent region does not exist.

        If the region_ref has a specified parent_region_id, check that
        the parent exists, otherwise, raise a NotFound.
        """
        #parent_region_id = region_ref.get('parent_region_id')
        #if parent_region_id is not None:
        #    # This will raise NotFound if the parent doesn't exist,
        #    # which is the behavior we want.
        #    self._get_region(session, parent_region_id)
        pass

    def _has_endpoints(self, region, root_region):
        #if region.endpoints is not None and len(region.endpoints) > 0:
        #    return True

        #q = session.query(Region)
        #q = q.filter_by(parent_region_id=region.id)
        #for child in q.all():
        #    if child.id == root_region.id:
        #        # Hit a circular region hierarchy
        #        return False
        #    if self._has_endpoints(session, child, root_region):
        #        return True
        #return False

        # We're not implementing hierarchical regions, and ignoring second
        # argument root_region
        try:
            ref = Endpoint.get(region_id=region.id)
        except DoesNotExist:
            return False
        except MultipleObjectsReturned:
            return True
        return True

    def get_region(self, region_id):
        #session = sql.get_session()
        #return self._get_region(session, region_id).to_dict()
        return self._get_region(region_id).to_dict()

    def delete_region(self, region_id):
        #session = sql.get_session()
        #with session.begin():
        #    ref = self._get_region(session, region_id)
        #    if self._has_endpoints(session, ref, ref):
        #        raise exception.RegionDeletionError(region_id=region_id)
        #    self._delete_child_regions(session, region_id, region_id)
        #    session.delete(ref)
        ref = self._get_region(region_id)
        if self._has_endpoints(ref, ref):
            raise exception.RegionDeletionError(region_id=region_id)
        ref.delete()

    #@sql.handle_conflicts(conflict_type='region')
    def create_region(self, region_ref):
        #session = sql.get_session()
        #with session.begin():
        #    self._check_parent_region(session, region_ref)
        #    region = Region.from_dict(region_ref)
        #    session.add(region)
        #return region.to_dict()
        try:
            ref = Region.get(id=region_ref['id'])
        except DoesNotExist:
            create_dict = Region.get_model_dict(region_ref)
            ref = Region.create(**create_dict)
            return ref.to_dict()

        raise exception.Conflict(conflict_type='region')

    def update_region(self, region_id, region_ref):
        #session = sql.get_session()
        #with session.begin():
        #    self._check_parent_region(session, region_ref)
        #    ref = self._get_region(session, region_id)
        #    old_dict = ref.to_dict()
        #    old_dict.update(region_ref)
        #    self._ensure_no_circle_in_hierarchical_regions(old_dict)
        #    new_region = Region.from_dict(old_dict)
        #    for attr in Region.attributes:
        #        if attr != 'id':
        #            setattr(ref, attr, getattr(new_region, attr))
        #return ref.to_dict()
        old_ref = self._get_region(region_id)
        old_dict = old_ref.to_dict()
        old_dict.update(region_ref)

        # Update region ID just in case somebody passed in a differnt region id
        # in the dict
        old_dict['region_id'] = region_id

        new_update_dict = Region.get_model_dict(old_dict)
        ref = Region.create(**new_update_dict)
        return ref.to_dict()

    # Services
    @cass.truncated
    def list_services(self, hints):
        #session = sql.get_session()
        #services = session.query(Service)
        #services = sql.filter_limit_query(Service, services, hints)
        #return [s.to_dict() for s in list(services)]

        # Ignore hints
        refs = Service.objects.all()
        return [ref.to_dict() for ref in refs]

    def _get_service(self, service_id):
        #ref = session.query(Service).get(service_id)
        #if not ref:
        #    raise exception.ServiceNotFound(service_id=service_id)
        #return ref

        try:
            ref = Service.get(id=service_id)
        except DoesNotExist:
            raise exception.ServiceNotFound(service_id=service_id)
        return ref

    def get_service(self, service_id):
        #session = sql.get_session()
        #return self._get_service(session, service_id).to_dict()

        return self._get_service(service_id).to_dict()

    def delete_service(self, service_id):
        #session = sql.get_session()
        #with session.begin():
        #    ref = self._get_service(session, service_id)
        #    session.query(Endpoint).filter_by(service_id=service_id).delete()
        #    session.delete(ref)
        service_ref = self._get_service(service_id)
        endpoint_refs = Endpoint.objects.filter(service_id=service_id)
        with BatchQuery(batch_type=BatchType.Unlogged) as b:
            # TODO(rushiagr):Find out of there is a direct way to delete refs by a query
            for ref in endpoint_refs:
                ref.batch(b).delete()
            service_ref.batch(b).delete()

    def create_service(self, service_id, service_ref):
        #session = sql.get_session()
        #with session.begin():
        #    service = Service.from_dict(service_ref)
        #    session.add(service)
        #return service.to_dict()
        create_dict = Service.get_model_dict(service_ref)
        ref = Service.create(**create_dict)
        return ref.to_dict()

    def update_service(self, service_id, service_ref):
        #session = sql.get_session()
        #with session.begin():
        #    ref = self._get_service(session, service_id)
        #    old_dict = ref.to_dict()
        #    old_dict.update(service_ref)
        #    new_service = Service.from_dict(old_dict)
        #    for attr in Service.attributes:
        #        if attr != 'id':
        #            setattr(ref, attr, getattr(new_service, attr))
        #    ref.extra = new_service.extra
        #return ref.to_dict()

        # NOTE(rushiagr): service_ref is a dict, not a ORM object
        ref = self._get_service(service_id)
        old_dict = ref.to_dict()
        old_dict.update(service_ref)
        # Updating service_id again just in case somebody passed in a dict
        # with a different id
        old_dict['id'] = service_id
        new_dict = Service.get_model_dict(old_dict)
        return Service.create(**new_dict).to_dict()

    # Endpoints
    def create_endpoint(self, endpoint_id, endpoint_ref):
        #session = sql.get_session()
        #new_endpoint = Endpoint.from_dict(endpoint_ref)

        #with session.begin():
        #    session.add(new_endpoint)
        #return new_endpoint.to_dict()
        new_endpoint = Endpoint.get_model_dict(endpoint_ref)
        ref = Endpoint.create(**new_endpoint)
        return ref.to_dict()

    def delete_endpoint(self, endpoint_id):
       # session = sql.get_session()
       # with session.begin():
       #     ref = self._get_endpoint(session, endpoint_id)
       #     session.delete(ref)
        ref = self._get_endpoint(endpoint_id)
        ref.delete()

    def _get_endpoint(self, endpoint_id):
        #try:
        #    return session.query(Endpoint).filter_by(id=endpoint_id).one()
        #except sql.NotFound:
        #    raise exception.EndpointNotFound(endpoint_id=endpoint_id)
        try:
            return Endpoint.get(id=endpoint_id)
        except DoesNotExist:
            raise exception.EndpointNotFound(endpoint_id=endpoint_id)

    def get_endpoint(self, endpoint_id):
        #session = sql.get_session()
        #return self._get_endpoint(session, endpoint_id).to_dict()
        return self._get_endpoint(endpoint_id).to_dict()

    @cass.truncated
    def list_endpoints(self, hints):
        # Ignore hints
        #session = sql.get_session()
        #endpoints = session.query(Endpoint)
        #endpoints = sql.filter_limit_query(Endpoint, endpoints, hints)
        #return [e.to_dict() for e in list(endpoints)]
        refs = Endpoint.objects.all()
        return [ref.to_dict() for ref in refs]

    def update_endpoint(self, endpoint_id, endpoint_ref):
        #session = sql.get_session()

        #with session.begin():
        #    ref = self._get_endpoint(session, endpoint_id)
        #    old_dict = ref.to_dict()
        #    old_dict.update(endpoint_ref)
        #    new_endpoint = Endpoint.from_dict(old_dict)
        #    for attr in Endpoint.attributes:
        #        if attr != 'id':
        #            setattr(ref, attr, getattr(new_endpoint, attr))
        #    ref.extra = new_endpoint.extra
        #return ref.to_dict()

        # NOTE(rushiagr): endpoint_ref is a dict, not a ORM object
        ref = self._get_endpoint(endpoint_id)
        old_dict = ref.to_dict()
        old_dict.update(endpoint_ref)
        # Updating endpoint_id again just in case somebody passed in a dict
        # with a different id
        old_dict['id'] = endpoint_id
        new_dict = Service.get_model_dict(old_dict)
        return Endpoint.create(**new_dict).to_dict()

    def get_catalog(self, user_id, tenant_id):
        """Retrieve and format the V2 service catalog.

        :param user_id: The id of the user who has been authenticated for
            creating service catalog.
        :param tenant_id: The id of the project. 'tenant_id' will be None
            in the case this being called to create a catalog to go in a
            domain scoped token. In this case, any endpoint that requires
            a tenant_id as part of their URL will be skipped (as would a whole
            service if, as a consequence, it has no valid endpoints).

        :returns: A nested dict representing the service catalog or an
                  empty dict.

        """

        # NOTE(rushiagr): super ugly code, proceed with caution. Just for
        # ease of comparison with sql driver, very little changes are
        # made to the quirks of sql driver implementation.
        substitutions = dict(
            itertools.chain(six.iteritems(CONF),
                            six.iteritems(CONF.eventlet_server)))
        substitutions.update({'user_id': user_id})
        silent_keyerror_failures = []
        if tenant_id:
            substitutions.update({'tenant_id': tenant_id})
        else:
            silent_keyerror_failures = ['tenant_id']

        #session = sql.get_session()
        #endpoints = (session.query(Endpoint).
        #             options(sql.joinedload(Endpoint.service)).
        #             filter(Endpoint.enabled == true()).all())

        # NOTE(rushiagr): Unlike SQL, we're just keeping the endpoint
        # reference here, and in the below 'for' loop, getting the details
        # of associated region and service
        endpoints = Endpoint.objects.filter(enabled=True)

        catalog = {}

        for endpoint in endpoints:
            service = self._get_service(endpoint.service_id)
            region = self._get_region(endpoint.region_id)
            #if not endpoint.service['enabled']:
            if not service.enabled:
                continue
            try:
                formatted_url = core.format_url(
                    endpoint.url, substitutions,
                    #endpoint['url'], substitutions,
                    silent_keyerror_failures=silent_keyerror_failures)
                if formatted_url is not None:
                    url = formatted_url
                else:
                    continue
            except exception.MalformedEndpoint:
                continue  # this failure is already logged in format_url()

            #region = endpoint['region_id']
            #service_type = endpoint.service['type']
            #default_service = {
            #    'id': endpoint['id'],
            #    'name': endpoint.service.extra.get('name', ''),
            #    'publicURL': ''
            #}
            region = region.id
            service_type = service.type
            service_dict = service.to_dict()
            default_service = {
                'id': endpoint.id,
                'name': service_dict['extra'].get('name', ''),
                'publicURL': ''
            }
            catalog.setdefault(region, {})
            catalog[region].setdefault(service_type, default_service)
            interface_url = '%sURL' % endpoint.interface
            catalog[region][service_type][interface_url] = url

        return catalog

    def get_v3_catalog(self, user_id, tenant_id):
        """Retrieve and format the current V3 service catalog.

        :param user_id: The id of the user who has been authenticated for
            creating service catalog.
        :param tenant_id: The id of the project. 'tenant_id' will be None in
            the case this being called to create a catalog to go in a domain
            scoped token. In this case, any endpoint that requires a
            tenant_id as part of their URL will be skipped.

        :returns: A list representing the service catalog or an empty list

        """
        d = dict(
            itertools.chain(six.iteritems(CONF),
                            six.iteritems(CONF.eventlet_server)))
        d.update({'user_id': user_id})
        silent_keyerror_failures = []
        if tenant_id:
            d.update({'tenant_id': tenant_id})
        else:
            silent_keyerror_failures = ['tenant_id']

        #session = sql.get_session()
        #services = (session.query(Service).filter(Service.enabled == true()).
        #            options(sql.joinedload(Service.endpoints)).
        #            all())

        services = Service.objects.filter(enabled=True)

        def make_v3_endpoints(endpoints):
            for endpoint in (ep.to_dict() for ep in endpoints if ep.enabled):
                del endpoint['service_id']
                del endpoint['legacy_endpoint_id']
                del endpoint['enabled']
                endpoint['region'] = endpoint['region_id']
                try:
                    formatted_url = core.format_url(
                        endpoint['url'], d,
                        silent_keyerror_failures=silent_keyerror_failures)
                    if formatted_url:
                        endpoint['url'] = formatted_url
                    else:
                        continue
                except exception.MalformedEndpoint:
                    continue  # this failure is already logged in format_url()

                yield endpoint

        # TODO(davechen): If there is service with no endpoints, we should skip
        # the service instead of keeping it in the catalog, see bug #1436704.
        def make_v3_service(svc):
            #eps = list(make_v3_endpoints(svc.endpoints))

            endpoints = Endpoint.objects.filter(service_id=svc.id)
            eps = list(make_v3_endpoints(endpoints))
            service = {'endpoints': eps, 'id': svc.id, 'type': svc.type}
            #service['name'] = svc.extra.get('name', '')
            service['name'] = svc.to_dict()['extra'].get('name', '')
            return service

        return [make_v3_service(svc) for svc in services]
