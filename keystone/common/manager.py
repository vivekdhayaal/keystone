# Copyright 2012 OpenStack Foundation
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

import abc
import functools

from oslo_log import log
from oslo_log import versionutils
from oslo_utils import importutils
import stevedore

from keystone import exception


LOG = log.getLogger(__name__)


def response_truncated(f):
    """Truncate the list returned by the wrapped function.

    This is designed to wrap Manager list_{entity} methods to ensure that
    any list limits that are defined are passed to the driver layer.  If a
    hints list is provided, the wrapper will insert the relevant limit into
    the hints so that the underlying driver call can try and honor it. If the
    driver does truncate the response, it will update the 'truncated' attribute
    in the 'limit' entry in the hints list, which enables the caller of this
    function to know if truncation has taken place.  If, however, the driver
    layer is unable to perform truncation, the 'limit' entry is simply left in
    the hints list for the caller to handle.

    A _get_list_limit() method is required to be present in the object class
    hierarchy, which returns the limit for this backend to which we will
    truncate.

    If a hints list is not provided in the arguments of the wrapped call then
    any limits set in the config file are ignored.  This allows internal use
    of such wrapped methods where the entire data set is needed as input for
    the calculations of some other API (e.g. get role assignments for a given
    project).

    """
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        if kwargs.get('hints') is None:
            return f(self, *args, **kwargs)

        list_limit = self.driver._get_list_limit()
        if list_limit:
            kwargs['hints'].set_limit(list_limit)
        return f(self, *args, **kwargs)
    return wrapper


def load_driver(namespace, driver_name, *args):
    try:
        driver_manager = stevedore.DriverManager(namespace,
                                                 driver_name,
                                                 invoke_on_load=True,
                                                 invoke_args=args)
        return driver_manager.driver
    except RuntimeError as e:
        LOG.debug('Failed to load %r using stevedore: %s', driver_name, e)
        # Ignore failure and continue on.

    @versionutils.deprecated(as_of=versionutils.deprecated.LIBERTY,
                             in_favor_of='entrypoints',
                             what='direct import of driver')
    def _load_using_import(driver_name, *args):
        return importutils.import_object(driver_name, *args)

    # For backwards-compatibility, an unregistered class reference can
    # still be used.
    return _load_using_import(driver_name, *args)


class Manager(object):
    """Base class for intermediary request layer.

    The Manager layer exists to support additional logic that applies to all
    or some of the methods exposed by a service that are not specific to the
    HTTP interface.

    It also provides a stable entry point to dynamic backends.

    An example of a probable use case is logging all the calls.

    """

    driver_namespace = None

    def __init__(self, driver_name):
        self.driver = load_driver(self.driver_namespace, driver_name)

    def __getattr__(self, name):
        """Forward calls to the underlying driver."""
        f = getattr(self.driver, name)
        setattr(self, name, f)
        return f


class CompatibilizerMeta(abc.ABCMeta):
    def __new__(metaclass, name, bases, attrs):
        INTERFACE_VERSION = None
        for cls in bases:
            try:
                INTERFACE_VERSION = int(cls.INTERFACE_VERSION)
                driverABC = cls
                break
            except AttributeError:
                # not a driver interface
                pass

        if INTERFACE_VERSION is not None:
            # code pertaining to driver implementations alone.
            # the following six lines of code are temporarily added
            # to ensure that existing drivers will work with next
            # release(VERSION=12); so these should be removed thereafter.
            DRIVER_VERSION = attrs.get("DRIVER_VERSION")
            if DRIVER_VERSION is None and INTERFACE_VERSION == 12:
                DRIVER_VERSION = 12
                LOG.debug('Warning: Version not specified in driver.'
                          'Such drivers would be supported only in this '
                          'release(version=12)')
            try:
                DRIVER_VERSION = int(DRIVER_VERSION)
            except TypeError:
                raise exception.IncompatibleDriver()
            if INTERFACE_VERSION == DRIVER_VERSION:
                # no compatibility issues
                pass
            elif INTERFACE_VERSION == DRIVER_VERSION + 1:
                # introduce the compatibility class for backward compatibility
                import inspect
                for tup in inspect.getmembers(driverABC.COMPATIBILIZER,
                                              predicate=inspect.ismethod):
                    attrs[tup[0]] = tup[1]
                for key in driverABC.__abstractmethods__:
                    if key not in attrs:
                        # developer missed to write compatibility code
                        # for not-implemented abstract method of driver
                        raise exception.IncompatibleInterface()
            else:
                # older versions are not supported
                raise exception.IncompatibleDriver()
        return super(CompatibilizerMeta, metaclass).__new__(metaclass, name,
                                                            bases, attrs)
