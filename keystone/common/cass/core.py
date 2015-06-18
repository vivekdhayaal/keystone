# Copyright 2015 Reliance Jio Infocomm
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

"""Cassandra!

To create keyspace by name keystone:

    from cassandra.cqlengine.management import create_keyspace
    create_keyspace("keystone", "SimpleStrategy", 1)
"""
from cassandra.cqlengine.models import Model, ModelMetaClass
from cassandra.cqlengine.named import NamedTable
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine import connection
from cassandra.policies import TokenAwarePolicy
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.policies import RetryPolicy

import functools
import json

from keystone import exception
from keystone.i18n import _

from oslo_log import log

LOG = log.getLogger(__name__)

ips=['127.0.0.1']
keyspace='keystone'

import six

@six.add_metaclass(ModelMetaClass)
class ExtrasModel(Model):
    __abstract__ = True

    @classmethod
    def get_model_dict(cls, d, extras_table=True):
        # 'extras_table' option is for working with tables which doesn't have extras
        # magic. For such tables, just pass extras_table=False
        new_dict = d.copy()

        if not extras_table:
            for k in new_dict.keys():
                if k not in cls._columns:
                    new_dict.pop(k)
            return new_dict

        new_dict['extra'] = json.dumps(dict((k, new_dict.pop(k)) for k in six.iterkeys(d)
                                if k not in cls._columns and k != 'extra'))
        return new_dict

    def to_dict(self):
        model_dict = {}
        for k, v in zip(self.keys(), self.values()):
            model_dict[k] = v

        if self.__class__.__name__ == 'RoleAssignment':
            return model_dict

        if 'extra' in model_dict.keys():
            model_dict['extra'] = json.loads(model_dict['extra'])

            for k, v in model_dict['extra'].items():
                model_dict[k] = v

        if self.__class__.__name__ == 'User':
            if 'default_project_id' in model_dict and model_dict['default_project_id'] is None:
                del model_dict['default_project_id']
        return model_dict


def truncated(f):
    """Ensure list truncation is detected in Driver list entity methods.

    This is designed to wrap and sql Driver list_{entity} methods in order to
    calculate if the resultant list has been truncated. Provided a limit dict
    is found in the hints list, we increment the limit by one so as to ask the
    wrapped function for one more entity than the limit, and then once the list
    has been generated, we check to see if the original limit has been
    exceeded, in which case we truncate back to that limit and set the
    'truncated' boolean to 'true' in the hints limit dict.

    """
    @functools.wraps(f)
    def wrapper(self, hints, *args, **kwargs):
        if not hasattr(hints, 'limit'):
            raise exception.UnexpectedError(
                _('Cannot truncate a driver call without hints list as '
                  'first parameter after self '))

        if hints.limit is None:
            return f(self, hints, *args, **kwargs)

        # A limit is set, so ask for one more entry than we need
        list_limit = hints.limit['limit']
        hints.set_limit(list_limit + 1)
        ref_list = f(self, hints, *args, **kwargs)

        # If we got more than the original limit then trim back the list and
        # mark it truncated.  In both cases, make sure we set the limit back
        # to its original value.
        if len(ref_list) > list_limit:
            hints.set_limit(list_limit, truncated=True)
            return ref_list[:list_limit]
        else:
            hints.set_limit(list_limit)
            return ref_list
    return wrapper

def get_exact_comparison_columns(hints):
    exact_comparison_columns_list = []
    filts = hints.filters
    for filt in filts:
        if filt['comparator'] == 'equals':
            exact_comparison_columns_list.append(filt['name'])
    return exact_comparison_columns_list

def is_secondary_idx_on_col(model_cls, column):
    IndexInfo = NamedTable("system", '"IndexInfo"')

    # For a table 'mytable', if a secondary index exist on column 'mycolumn',
    # the index name in "IndexInfo" table will be
    # 'mytable.index_mytable_mycolumn'
    index_name=model_cls.__table_name__ + '.' + \
            'index_' + model_cls.__table_name__ + '_' + column
    try:
        ix_ref = IndexInfo.objects.get(table_name=keyspace,
                index_name=index_name)
    except DoesNotExist:
        # NOTE(rushiagr): there are two more columns 'enabled' and 'name'
        # in 'user' table
        # where hints are not being filtered by the driver, but we never
        # noticed that as the controller was doing the filtering anyway.
        # We noticed the issue only in case of list_users and list_groups
        # only because there is a bug in keystone -- at one place, these
        # two methods are used 'bare', i.e., these methods are called
        # directly, without calling the methods which anyway filter
        # if the driver methods don't filter
        return False

    return True

def handle_conflicts(conflict_type='object'):
    """Converts select sqlalchemy exceptions into HTTP 409 Conflict."""
    _conflict_msg = 'Conflict %(conflict_type)s: %(details)s'

    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except exception.Conflict as e:
                # LOG the exception for debug purposes, do not send the
                # exception details out with the raised Conflict exception
                # as it can contain raw SQL.
                LOG.debug(_conflict_msg, {'conflict_type': conflict_type,
                                          'details': six.text_type(e)})
                raise exception.Conflict(type=conflict_type,
                                         details=_('Duplicate Entry'))

        return wrapper
    return decorator

class QuorumFallBackRetryPolicy(RetryPolicy):
    def on_unavailable(self, query, consistency, required_replicas, alive_replicas, retry_num):
        if retry_num != 0:
            return (self.RETHROW, None)
        else:
            if ConsistencyLevel.LOCAL_QUORUM == consistency:
                return (self.RETRY, ConsistencyLevel.QUORUM)
            else:
                return (self.RETHROW, None)

def connect_to_cluster(ips, keyspace):
    return connection.setup(ips, keyspace, consistency = ConsistencyLevel.LOCAL_QUORUM, 
                            load_balancing_policy = TokenAwarePolicy(DCAwareRoundRobinPolicy()),
                            default_retry_policy = QuorumFallBackRetryPolicy())
