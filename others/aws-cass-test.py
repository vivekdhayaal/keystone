# http://datastax.github.io/python-driver/object_mapper.html
import numpy as np
import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from datetime import datetime
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model

class ExampleModel(Model):
    example_id      = columns.UUID(primary_key=True, default=uuid.uuid4)
    example_type    = columns.Integer(index=True)
    created_at      = columns.DateTime()
    description     = columns.Text(required=False)

connection.setup(['52.74.230.111', '54.169.112.143'], "keystone", protocol_version=3)

sync_table(ExampleModel)

### Eventlet
# URL: https://datastax.github.io/python-driver/cqlengine/third_party.html
import eventlet
#pool = eventlet.GreenPool()
a = eventlet.greenthread.spawn(ExampleModel.create, example_type=1, description=str(2), created_at=datetime.now())
#b = pool.spawn(ExampleModel.create, example_type=1, description=str(2), created_at=datetime.now())
#a.wait()
#b.wait()
