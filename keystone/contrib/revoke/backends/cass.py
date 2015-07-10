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

from oslo_utils import timeutils
from oslo_config import cfg

from keystone.common import cass
from keystone.contrib import revoke
from keystone.contrib.revoke import model

from cassandra.cqlengine import columns
from cassandra.cqlengine.functions import MinTimeUUID, MaxTimeUUID
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.query import BatchQuery
from cassandra.cqlengine.query import BatchType

import datetime

CONF = cfg.CONF

class RevocationEvent(cass.ExtrasModel):
    # NOTE(rushiagr): We are creating buckets of one hour each.
    # So if an event is revoked at 6:12 PM, it's going to go into the
    # 6PM bucket -- the bucket which contains all revocation events
    # which expire between 6PM and 7PM, not including 7PM.
    revoked_hour = columns.Text(primary_key=True)
    revoked_at = columns.TimeUUID(primary_key=True, required=True)
    domain_id = columns.Text(max_length=64)
    project_id = columns.Text(max_length=64)
    user_id = columns.Text(max_length=64)
    role_id = columns.Text(max_length=64)
    trust_id = columns.Text(max_length=64)
    consumer_id = columns.Text(max_length=64)
    access_token_id = columns.Text(max_length=64)
    issued_before = columns.DateTime(required=True)
    expires_at = columns.DateTime()
    audit_id = columns.Text(max_length=32)
    audit_chain_id = columns.Text(max_length=32)

cass.connect_to_cluster()

sync_table(RevocationEvent)

class Revoke(revoke.Driver):
    def list_events(self, last_fetch=None):
        # get the oldest time when an entry will be present in the db
        oldest = revoke.revoked_before_cutoff_time()

        now_time = timeutils.utcnow()
        now_time_hour = now_time.replace(minute=0, second=0, microsecond=0)

        #NOTE(rushiagr): Note that we're using last_fetch only to find the
        # last cassandra partition to query. We're not exactly returning
        # only rows later than the last_fetch time, but _all_ rows from
        # partition in which the last_fetch time comes (along with rows
        # from partitions with a later time)
        if last_fetch is not None and last_fetch < oldest:
            last_fetch = oldest
        oldest_time = (now_time - (now_time - oldest)) if last_fetch is None else last_fetch
        oldest_time_hour = oldest_time.replace(minute=0, second=0, microsecond=0)

        hour_list = []  # List of hour intervals we will have to query

        current_hour = now_time_hour
        while True:
            hour_list.append(current_hour)
            if oldest_time_hour == current_hour:
                break
            else:
                current_hour = current_hour - datetime.timedelta(hours=1)


        refs_list = []
        for hour in hour_list:
            refs = RevocationEvent.filter(revoked_hour=hour.isoformat())
            refs_list.append(refs)

        events = []
        for refs in refs_list:
            events.extend([model.RevokeEvent(**e.to_dict()) for e in refs])
        return events

    def revoke(self, event):
        kwargs = dict()
        for attr in model.REVOKE_KEYS:
            kwargs[attr] = getattr(event, attr)
        # revoked_at is of format datetime.utcnow(), so splitting at first
        # colon will give us the date and hour
        kwargs['revoked_hour'] = event.revoked_at.replace(minute=0, second=0,
                microsecond=0).isoformat()
        kwargs['revoked_at'] = columns.TimeUUID.from_datetime(kwargs['revoked_at'])
        ttl_seconds=CONF.token.expiration + CONF.revoke.expiration_buffer
        RevocationEvent.ttl(ttl_seconds).create(**kwargs)
