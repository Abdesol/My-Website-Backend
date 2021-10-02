from pony.orm import *
import datetime

db = Database()
db.bind(provider='sqlite', filename='database.sqlite', create_db=True)


class Blog(db.Entity):
    title = Required(str)
    slug = Required(str, unique=True)
    description = Required(str)
    content = Required(str)
    date = Required(datetime.datetime)

class Project(db.Entity):
    title = Required(str)
    description = Required(str)
    github = Required(str)
    img = Required(str)

class Certificate(db.Entity):
    name = Required(str)
    src = Required(str)


db.generate_mapping(create_tables=True)
