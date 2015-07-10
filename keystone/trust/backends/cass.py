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

import time

from oslo_log import log
from oslo_utils import timeutils
from six.moves import range

from keystone.common import cass
from keystone import exception
from keystone import trust

from cassandra.cqlengine import columns
from cassandra.cqlengine.query import LWTException
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.management import sync_table

LOG = log.getLogger(__name__)
# The maximum number of iterations that will be attempted for optimistic
# locking on consuming a limited-use trust.
MAXIMUM_CONSUME_ATTEMPTS = 10

class TrustModel(cass.ExtrasModel):
    id = columns.Text(primary_key=True, max_length=64)
    # user id of owner
    trustor_user_id = columns.Text(max_length=64, index=True, required=True)
    # user_id of user allowed to consume this preauth
    trustee_user_id = columns.Text(max_length=64, index=True, required=True)
    project_id = columns.Text(max_length=64)
    impersonation = columns.Boolean(required=True)
    is_deleted = columns.Boolean(default=False, index=True)
    deleted_at = columns.DateTime()
    expires_at = columns.DateTime()
    remaining_uses = columns.Integer(index=True)
    extra = columns.Text(default='')
    roles = columns.Set(columns.Text)

cass.connect_to_cluster()

sync_table(TrustModel)


class Trust(trust.Driver):
    def create_trust(self, trust_id, trust, roles):
        try:
            TrustModel.get(id=trust_id)
            # we are here means, a trust of same id already exists
            # so raise exception
            # LOG the exception for debug purposes
            conflict_type = 'trust'
            details = 'duplicate entry'
            _conflict_msg = 'Conflict %(conflict_type)s: %(details)s'
            LOG.debug(_conflict_msg, {'conflict_type': conflict_type,
                                      'details': details})
            raise exception.Conflict(type=conflict_type,
                                     details=_(details))
        except DoesNotExist:
            trust['id'] = trust_id
            if trust.get('expires_at') and trust['expires_at'].tzinfo is not None:
                trust['expires_at'] = timeutils.normalize_time(trust['expires_at'])
            role_set = set([])
            for role in roles:
                role_set.add(role['id'])
            trust['roles'] = role_set
            create_dict = TrustModel.get_model_dict(trust)
            ref = TrustModel.create(**create_dict)
            return ref.to_dict()

    def consume_use(self, trust_id):
        for attempt in range(MAXIMUM_CONSUME_ATTEMPTS):
            trust = self._get_trust(trust_id)
            remaining_uses = trust.get('remaining_uses')
            if remaining_uses is None:
                # unlimited uses, do nothing
                break
            elif remaining_uses > 0:
                # NOTE(morganfainberg): use an optimistic locking method
                # to ensure we only ever update a trust that has the
                # expected number of remaining uses.
                try:
                    TrustModel.iff(id=trust_id, is_deleted=False, remaining_uses=remaining_uses).update(remaining_uses=(remaining_uses - 1))
                    # Successfully consumed a single limited-use trust.
                    break
                except LWTException as e:
                    # update wasn't applied. so continue
                    continue
            else:
                raise exception.TrustUseLimitReached(trust_id=trust_id)
            # NOTE(morganfainberg): Ensure we have a yield point for eventlet
            # here. This should cost us nothing otherwise. This can be removed
            # if/when oslo.db cleanly handles yields on db calls.
            time.sleep(0)
        else:
            # NOTE(morganfainberg): In the case the for loop is not prematurely
            # broken out of, this else block is executed. This means the trust
            # was not unlimited nor was it consumed (we hit the maximum
            # iteration limit). This is just an indicator that we were unable
            # to get the optimistic lock rather than silently failing or
            # incorrectly indicating a trust was consumed.
            raise exception.TrustConsumeMaximumAttempt(trust_id=trust_id)

    def _get_trust(self, trust_id, deleted=False):
        try:
            if not deleted:
                ref = TrustModel.get(id=trust_id, is_deleted=deleted)
            else:
                ref = TrustModel.get(id=trust_id)
        except DoesNotExist:
            raise exception.TrustNotFound(trust_id=trust_id)
        return ref.to_dict()

    def get_trust(self, trust_id, deleted=False):
        trust = self._get_trust(trust_id, deleted)
        if trust.get('expires_at') is not None and not deleted:
            now = timeutils.utcnow()
            if now > trust['expires_at']:
                raise exception.TrustNotFound(trust_id=trust_id)
        # Do not return trusts that can't be used anymore
        if trust.get('remaining_uses') is not None and not deleted:
            if trust['remaining_uses'] <= 0:
                raise exception.TrustNotFound(trust_id=trust_id)
        roles = []
        for role in trust['roles']:
            roles.append({'id' : role})
        trust['roles'] = roles
        return trust

    def list_trusts(self):
        refs = TrustModel.objects().filter(is_deleted=False)
        return [ref.to_dict() for ref in refs]

    def list_trusts_for_trustee(self, trustee_user_id):
        refs = TrustModel.objects().filter(is_deleted=False, trustee_user_id=trustee_user_id).allow_filtering()
        return [ref.to_dict() for ref in refs]

    def list_trusts_for_trustor(self, trustor_user_id):
        refs = TrustModel.objects().filter(is_deleted=False, trustor_user_id=trustor_user_id).allow_filtering()
        return [ref.to_dict() for ref in refs]

    def delete_trust(self, trust_id):
        TrustModel.objects(id=trust_id).update(is_deleted=True, deleted_at=timeutils.utcnow())
