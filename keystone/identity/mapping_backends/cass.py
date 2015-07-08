# Copyright 2014 IBM Corp.
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
from keystone.common import dependency
from keystone import identity
from keystone.identity.mapping_backends import mapping as identity_mapping

from cassandra.cqlengine import columns
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import BatchType, DoesNotExist

CONF = cfg.CONF


class IDMapping(cass.ExtrasModel):
    __table_name__ = 'id_mapping'
    # NOTE(rushiagr): We have created a secondary index on each of
    # domain_id, local_id and entity_type columns, just so that
    # we can 'efficiently filter' while PURGING them. This might not
    # be the best way, and we can just in-memory filter and get away with
    # it. What we're doing here is storing data in three indices for each
    # insert separate from the original table. And don't forget that
    # these indices are only referred to when purging -- the deletion
    # operation -- and in that only when 'some' filters are specified!
    public_id = columns.Text(primary_key=True, max_length=64)
    domain_id = columns.Text(max_length=64, index=True)
    local_id = columns.Text(max_length=64, index=True)
    entity_type = columns.Text(max_length=64, index=True)
    # NOTE(rushiagr): make sure we follow the unique constraint of SQL:
    # domain_id, local_id, and entity_type combination should be unique
    # Remove this comment once this is done

    # NOTE(rushiagr): it seems there was a unique constraint in the SQL
    # driver, on columns domain_id, local_id, and entity_type, but
    # in the create method, the exception which would have been thrown
    # in case of a conflict/duplicate entry was not handled by using a
    # handle_conflicts decorator. Strange. Bug?

class IDMappingGSI(cass.ExtrasModel):
    __table_name__ = 'id_mapping_gsi'
    domain_id = columns.Text(primary_key=True, partition_key=True, max_length=64)
    local_id = columns.Text(primary_key=True, partition_key=True, max_length=64)
    entity_type = columns.Text(primary_key=True, partition_key=True, max_length=64)
    public_id = columns.Text(max_length=64)

cass.connect_to_cluster()

sync_table(IDMapping)
sync_table(IDMappingGSI)

@dependency.requires('id_generator_api')
class Mapping(identity.MappingDriver):

    def get_public_id(self, local_entity):
        # NOTE(rushiagr): First read henry-nash's comment below and then read
        # further. So basically, we can make some changes to some
        # configurations, e.g. generates_uuids() method, is_sql() and
        # make our driver not put UUID as public_id, but get that from
        # the sha256 hash of three values domain_id, local_id and
        # entity_type. But doing so requires so many changes, and verification
        # that I think for now we can just make do with an additional
        # table acting as GSI.

        # NOTE(henry-nash): Since the Public ID is regeneratable, rather
        # than search for the entry using the local entity values, we
        # could create the hash and do a PK lookup.  However this would only
        # work if we hashed all the entries, even those that already generate
        # UUIDs, like SQL.  Further, this would only work if the generation
        # algorithm was immutable (e.g. it had always been sha256).

        #session = sql.get_session()
        #query = session.query(IDMapping.public_id)
        #query = query.filter_by(domain_id=local_entity['domain_id'])
        #query = query.filter_by(local_id=local_entity['local_id'])
        #query = query.filter_by(entity_type=local_entity['entity_type'])
        #try:
        #    public_ref = query.one()
        #    public_id = public_ref.public_id
        #    return public_id
        #except sql.NotFound:
        #    return None

        try:
            ref = IDMappingGSI.get(domain_id=local_entity['domain_id'],
                    local_id=local_entity['local_id'],
                    entity_type=local_entity['entity_type'])
            return ref.public_id
        except DoesNotExist:
            return None


    def get_id_mapping(self, public_id):
        #session = sql.get_session()
        #mapping_ref = session.query(IDMapping).get(public_id)
        #if mapping_ref:
        #    return mapping_ref.to_dict()
        try:
            ref = IDMapping.get(public_id=public_id)
            return ref.to_dict()
        except DoesNotExist:
            pass

    def create_id_mapping(self, local_entity, public_id=None):
        #entity = local_entity.copy()
        #with sql.transaction() as session:
        #    if public_id is None:
        #        public_id = self.id_generator_api.generate_public_ID(entity)
        #    entity['public_id'] = public_id
        #    mapping_ref = IDMapping.from_dict(entity)
        #    session.add(mapping_ref)
        #return public_id

        entity = local_entity.copy()  # NOTE(rushiagr): Unsure why this is reqd

        if public_id is None:
            public_id = self.id_generator_api.generate_public_ID(entity)
        entity['public_id'] = public_id

        idmapping_create_dict = IDMapping.get_model_dict(entity)
        # Same column names for both tables, so no need to create another
        # dict, and can just re-use entity dict
        idmapping_gsi_create_dict = IDMappingGSI.get_model_dict(entity)

        IDMapping.create(**idmapping_create_dict)
        IDMappingGSI.create(**idmapping_gsi_create_dict)

        return public_id

    def delete_id_mapping(self, public_id):
        #with sql.transaction() as session:
        #    try:
        #        session.query(IDMapping).filter(
        #            IDMapping.public_id == public_id).delete()
        #    except sql.NotFound:
        #        # NOTE(morganfainberg): There is nothing to delete and nothing
        #        # to do.
        #        pass
        try:
            ref = IDMapping.get(public_id=public_id)
            IDMappingGSI(domain_id=ref.domain_id,
                    local_id=ref.local_id,
                    entity_type=ref.entity_type).delete()
            ref.delete()
        except DoesNotExist:
            pass


    def purge_mappings(self, purge_filter):
        #session = sql.get_session()
        #query = session.query(IDMapping)
        #if 'domain_id' in purge_filter:
        #    query = query.filter_by(domain_id=purge_filter['domain_id'])
        #if 'public_id' in purge_filter:
        #    query = query.filter_by(public_id=purge_filter['public_id'])
        #if 'local_id' in purge_filter:
        #    query = query.filter_by(local_id=purge_filter['local_id'])
        #if 'entity_type' in purge_filter:
        #    query = query.filter_by(entity_type=purge_filter['entity_type'])
        #query.delete()

        if 'public_id' in purge_filter:
            # NOTE(rushiagr): there is this one case when someone specifies
            # a public_id along with another filter. We're just ignoring
            # the other filter in such a case as we can uniquely
            # identify a DB record using only public_id
            try:
                ref = IDMapping.get(public_id=purge_filter['public_id'])
                IDMappingGSI(domain_id=ref.domain_id,
                        local_id=ref.local_id,
                        entity_type=ref.entity_type).delete()
                ref.delete()
            except DoesNotExist:
                pass

        elif not purge_filter or len(purge_filter) == 0:
            # TODO(rushiagr): can directly truncate the table, but it's
            # not supported by cqlengine as of now, as far as I know.
            # We might still do a truncate, using the cluster.truncate
            # method of the Python driver, but that would require
            # additional information e.g. connection IPs etc, so skipping
            # it for now
            refs = IDMapping.objects.all()
            for ref in refs:
                IDMappingGSI(domain_id=ref.domain_id,
                        local_id=ref.local_id,
                        entity_type=ref.entity_type).delete()
                ref.delete()

        elif (len(purge_filter) == 3 and set(purge_filter.keys()) ==
                set(['domain_id', 'local_id', 'entity_type'])):
            try:
                gsi_ref = IDMappingGSI.get(domain_id=purge_filter['domain_id'],
                        local_id=purge_filter['local_id'],
                        entity_type=purge_filter['entity_type'])
                gsi_ref.delete()
                IDMapping(public_id=gsi_ref.public_id).delete()
            except DoesNotExist:
                return

        else:
            # NOTE(rushiagr): We are filtering based on any one of the supplied
            # filters here. And then from the returned list, we're filtering
            # in-memory based on any more filters, if provided. We could
            # have also used CQL's ALLOW_FILTERING to let cassandra
            # handle the in-memory filtering.
            keys = purge_filter.keys()
            filt = {keys[0]: purge_filter[keys[0]]}
            refs = IDMapping.objects.filter(**filts)
            for ref in refs:
                ref_matches = True
                for key in keys:
                    if getattr(ref, key) != purge_filter[key]:
                        ref_matches = False
                if ref_matches:
                    gsi_ref = IDMappingGSI.get(domain_id=ref.domain_id,
                            local_id=ref.local_id,
                            entity_type=ref.entity_type)
                    gsi_ref.delete()
                    ref.delete()
