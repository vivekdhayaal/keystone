# Copyright 2015 Reliance Jio Infocomm Ltd.
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
from keystone.contrib import revoke
from keystone.contrib.revoke import model

from cassandra.cqlengine import columns
from cassandra.cqlengine.functions import MinTimeUUID, MaxTimeUUID
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.query import BatchQuery
from cassandra.cqlengine.query import BatchType


class RevocationEvent(cass.ExtrasModel):
    domain_id = columns.Text(max_length=64)
    project_id = columns.Text(max_length=64)
    user_id = columns.Text(max_length=64)
    role_id = columns.Text(max_length=64)
    trust_id = columns.Text(max_length=64)
    consumer_id = columns.Text(max_length=64)
    access_token_id = columns.Text(max_length=64)
    issued_before = columns.DateTime(required=True)
    expires_at = columns.DateTime()
    revoked_at = columns.TimeUUID(primary_key=True, required=True)
    audit_id = columns.Text(max_length=32)
    audit_chain_id = columns.Text(max_length=32)

cass.connect_to_cluster(cass.ips, cass.keyspace)

sync_table(RevocationEvent)

class Revoke(revoke.Driver):
    def _prune_expired_events(self):
        oldest = revoke.revoked_before_cutoff_time()
        refs = RevocationEvent.filter(revoked_at__lt=MaxTimeUUID(oldest))
        with BatchQuery(batch_type=BatchType.Unlogged) as b:
            for ref in refs:
                ref.batch(b).delete()

    def list_events(self, last_fetch=None):
        self._prune_expired_events()

        if last_fetch:
            refs = RevocationEvent.filter(revoked_at__gt=MinTimeUUID(last_fetch)).order_by("revoked_at")
        else:
            refs = RevocationEvent.objects.all().order_by("revoked_at")

        events = [model.RevokeEvent(**e.to_dict()) for e in refs]

        return events

    def revoke(self, event):
        kwargs = dict()
        for attr in model.REVOKE_KEYS:
            kwargs[attr] = getattr(event, attr)
        RevocationEvent.create(**kwargs)
