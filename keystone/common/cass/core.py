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

import functools
import json

from keystone import exception

ips=['127.0.0.1']
keyspace='keystone'

import six

@six.add_metaclass(ModelMetaClass)
class ExtrasModel(Model):
    __abstract__ = True

    @classmethod
    def get_model_dict(cls, d, extras_table=True):
        # 'extras_table' is for working with tables which doesn't have extras
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

def _filter(model, query, hints):
    """Applies filtering to a query.

    :param model: the table model in question
    :param query: query to apply filters to
    :param hints: contains the list of filters yet to be satisfied.
                  Any filters satisfied here will be removed so that
                  the caller will know if any filters remain.

    :returns query: query, updated with any filters satisfied

    """
    def inexact_filter(model, query, filter_, satisfied_filters):
        """Applies an inexact filter to a query.

        :param model: the table model in question
        :param query: query to apply filters to
        :param dict filter_: describes this filter
        :param list satisfied_filters: filter_ will be added if it is
                                       satisfied.

        :returns query: query updated to add any inexact filters we could
                        satisfy

        """
        column_attr = getattr(model, filter_['name'])

        # TODO(henry-nash): Sqlalchemy 0.7 defaults to case insensitivity
        # so once we find a way of changing that (maybe on a call-by-call
        # basis), we can add support for the case sensitive versions of
        # the filters below.  For now, these case sensitive versions will
        # be handled at the controller level.

        if filter_['case_sensitive']:
            return query

        if filter_['comparator'] == 'contains':
            query_term = column_attr.ilike('%%%s%%' % filter_['value'])
        elif filter_['comparator'] == 'startswith':
            query_term = column_attr.ilike('%s%%' % filter_['value'])
        elif filter_['comparator'] == 'endswith':
            query_term = column_attr.ilike('%%%s' % filter_['value'])
        else:
            # It's a filter we don't understand, so let the caller
            # work out if they need to do something with it.
            return query

        satisfied_filters.append(filter_)
        return query.filter(query_term)

    def exact_filter(model, filter_, cumulative_filter_dict):
        """Applies an exact filter to a query.

        :param model: the table model in question
        :param dict filter_: describes this filter
        :param dict cumulative_filter_dict: describes the set of exact filters
                                            built up so far

        """
        key = filter_['name']
        if isinstance(getattr(model, key).property.columns[0].type,
                      sql.types.Boolean):
            cumulative_filter_dict[key] = (
                utils.attr_as_boolean(filter_['value']))
        else:
            cumulative_filter_dict[key] = filter_['value']

    filter_dict = {}
    satisfied_filters = []
    for filter_ in hints.filters:
        if filter_['name'] not in model.attributes:
            continue
        if filter_['comparator'] == 'equals':
            exact_filter(model, filter_, filter_dict)
            satisfied_filters.append(filter_)
        else:
            query = inexact_filter(model, query, filter_, satisfied_filters)

    # Apply any exact filters we built up
    if filter_dict:
        query = query.filter_by(**filter_dict)

    # Remove satisfied filters, then the caller will know remaining filters
    for filter_ in satisfied_filters:
        hints.filters.remove(filter_)

    return query


def _limit(query, hints):
    """Applies a limit to a query.

    :param query: query to apply filters to
    :param hints: contains the list of filters and limit details.

    :returns updated query

    """
    # NOTE(henry-nash): If we were to implement pagination, then we
    # we would expand this method to support pagination and limiting.

    # If we satisfied all the filters, set an upper limit if supplied
    if hints.limit:
        query = query.limit(hints.limit['limit'])
    return query


def filter_limit_query(model, query, hints):
    """Applies filtering and limit to a query.

    :param model: table model
    :param query: query to apply filters to
    :param hints: contains the list of filters and limit details.  This may
                  be None, indicating that there are no filters or limits
                  to be applied. If it's not None, then any filters
                  satisfied here will be removed so that the caller will
                  know if any filters remain.

    :returns: updated query

    """
    if hints is None:
        return query

    # First try and satisfy any filters
    query = _filter(model, query, hints)

    # NOTE(henry-nash): Any unsatisfied filters will have been left in
    # the hints list for the controller to handle. We can only try and
    # limit here if all the filters are already satisfied since, if not,
    # doing so might mess up the final results. If there are still
    # unsatisfied filters, we have to leave any limiting to the controller
    # as well.

    if not hints.filters:
        return _limit(query, hints)
    else:
        return query
