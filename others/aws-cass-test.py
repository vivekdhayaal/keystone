# http://datastax.github.io/python-driver/object_mapper.html
import numpy as np
import uuid
import os

from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from datetime import datetime
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
import eventlet

from cassandra.policies import TokenAwarePolicy
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.policies import RetryPolicy
from cassandra import ConsistencyLevel

import functools
import json

class ExampleModel(Model):
    example_id      = columns.UUID(primary_key=True, default=uuid.uuid4)
    example_type    = columns.Integer(index=True)
    created_at      = columns.DateTime()
    description     = columns.Text(required=False)


class QuorumFallBackRetryPolicy(RetryPolicy):
    def on_unavailable(self, query, consistency, required_replicas, alive_replicas, retry_num):
        if retry_num != 0:
            return (self.RETHROW, None)
        else:
            if ConsistencyLevel.LOCAL_QUORUM == consistency:
                return (self.RETRY, ConsistencyLevel.QUORUM)
            else:
                return (self.RETHROW, None)

keyspace='keystone'
def connect_to_cluster():
    policy = DCAwareRoundRobinPolicy(local_dc='DC2')
    ips = ['52.74.230.111']
    return connection.setup(ips, keyspace, consistency = ConsistencyLevel.LOCAL_QUORUM,
                            load_balancing_policy = TokenAwarePolicy(policy),
                            default_retry_policy = QuorumFallBackRetryPolicy())

connect_to_cluster()
pid = os.fork()

#connection.setup(['52.74.230.111'], "keystone", protocol_version=3)

#sync_table(ExampleModel)



### Eventlet
# URL: https://datastax.github.io/python-driver/cqlengine/third_party.html
#pool = eventlet.GreenPool(1)
#a = eventlet.greenthread.spawn(ExampleModel.create, example_type=1, description=str(2), created_at=datetime.now())
#b = pool.spawn(loop_create1)
#c = pool.spawn(loop_create)
#a.wait()
#b.wait()
#c.wait()

def meth():
    print 'start of meth'
    print os.getpid(), os.getppid()
    print 'start of meth END'
    results = ExampleModel.objects.filter(example_type='1')
    print results.first()

#pool = eventlet.GreenPool(1)
#
#for i in range(3):
#    a = pool.spawn_n(meth)

#for i in range(3):
#    a.wait()

#if pid==0:
meth()
for i in range(10):
    meth()

#class QuorumFallBackRetryPolicy(RetryPolicy):
#    def on_unavailable(self, query, consistency, required_replicas, alive_replicas, retry_num):
#        if retry_num != 0:
#            return (self.RETHROW, None)
#        else:
#            if ConsistencyLevel.LOCAL_QUORUM == consistency:
#                return (self.RETRY, ConsistencyLevel.QUORUM)
#            else:
#                return (self.RETHROW, None)
#
#def connect_to_cluster():
#    if CONF.local_datacenter is not None:
#        policy = DCAwareRoundRobinPolicy(local_dc=CONF.local_datacenter)
#    else:
#        policy = DCAwareRoundRobinPolicy()
#    if CONF.cassandra_nodes_ips is not None:
#        ips = CONF.cassandra_nodes_ips.split(",")
#    else:
#        ips = ['127.0.0.1']
#
#    return connection.setup(ips, keyspace, consistency = ConsistencyLevel.LOCAL_QUORUM, 
#                            load_balancing_policy = TokenAwarePolicy(policy),
#                            default_retry_policy = QuorumFallBackRetryPolicy())
