# Copyright 2014 Reliance Jio Infocomm Ltd.
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

from keystone.common import cass
from keystone import exception

from cassandra.cqlengine import columns
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.management import sync_table


class PolicyAssociation(cass.ExtrasModel):
    # (endpoint_id, service_id, region_id) can be null
    endpoint_id = columns.Text(primary_key=True, partition_key=True,
                               index=True, max_length=64, default='null')
    service_id = columns.Text(primary_key=True, partition_key=True,
                              index=True, max_length=64, default='null')
    region_id = columns.Text(primary_key=True, partition_key=True,
                             index=True, max_length=64, default='null')
    policy_id = columns.Text(required=True, index=True, max_length=64)

cass.connect_to_cluster(cass.ips, cass.keyspace)

sync_table(PolicyAssociation)

# (endpoint_id, service_id, region_id) together form the primary key.
# But they aren't mandatory params. So, when any of them aren't provided,
# use 'null' value in their place.
def process_args(func):
    def wrapper(*args, **kwargs):
        args = tuple(args[i] if args[i] is not None else 'null' for i in xrange(len(args)))
        for key in kwargs:
            if kwargs[key] is None:
                kwargs[key] = 'null'
        return func(*args, **kwargs)
    return wrapper

class EndpointPolicy(object):

    @process_args
    def create_policy_association(self, policy_id, endpoint_id='null',
                                  service_id='null', region_id='null'):
        PolicyAssociation.objects(endpoint_id=endpoint_id,
                                   service_id=service_id,
                              region_id=region_id).update(policy_id=policy_id)

    @process_args
    def check_policy_association(self, policy_id, endpoint_id='null',
                                 service_id='null', region_id='null'):
        if PolicyAssociation.objects(endpoint_id=endpoint_id,
                               service_id=service_id, region_id=region_id,
                               policy_id=policy_id).count() == 0:
            raise exception.PolicyAssociationNotFound()

    @process_args
    def delete_policy_association(self, policy_id, endpoint_id='null',
                                  service_id='null', region_id='null'):
        try:
            # "DELETE from <table> WHERE ..." query doesn't accept
            # non-primary key columns in where clause. 
            # So, fetch the object first and then delete it.
            ref = PolicyAssociation.get(endpoint_id=endpoint_id,
                                   service_id=service_id, region_id=region_id,
                                   policy_id=policy_id)
            ref.delete()
        except DoesNotExist:
            raise exception.PolicyAssociationNotFound()

    @process_args
    def get_policy_association(self, endpoint_id='null',
                               service_id='null', region_id='null'):
        try:
            ref = PolicyAssociation.get(endpoint_id=endpoint_id,
                               service_id=service_id, region_id=region_id)
            return {'policy_id': ref.to_dict()['policy_id']}
        except DoesNotExist:
            raise exception.PolicyAssociationNotFound()

    def list_associations_for_policy(self, policy_id):
        refs = PolicyAssociation.objects(policy_id=policy_id)
        return [ref.to_dict() for ref in refs]

    def delete_association_by_endpoint(self, endpoint_id):
        for ref in PolicyAssociation.objects(endpoint_id=endpoint_id):
            ref.delete()

    def delete_association_by_service(self, service_id):
        for ref in PolicyAssociation.objects(service_id=service_id):
            ref.delete()

    def delete_association_by_region(self, region_id):
        for ref in PolicyAssociation.objects(region_id=region_id):
            ref.delete()

    def delete_association_by_policy(self, policy_id):
        for ref in PolicyAssociation.objects(policy_id=policy_id):
            ref.delete()
