from db import *
import db
db.filename = 'test.db'

db._clear_db()
create_db()
insert_job_instance('hasdf id', 'hello')
list_job_instances()