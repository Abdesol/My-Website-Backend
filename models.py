from enum import unique
from pony.orm import *
import datetime

db = Database()
db.bind(provider='sqlite', filename='Database/database.sqlite', create_db=True)


class Blog(db.Entity):
    title = Required(str)
    description = Required(str)
    url = Required(str)
    likes = Optional(int)
    img = Required(str)

class Project(db.Entity):
    title = Required(str)
    description = Required(str)
    github = Required(str)
    img = Required(str)
    likes = Optional(int)

class Certificate(db.Entity):
    name = Required(str)
    src = Required(str)
    likes = Optional(int)
    url = Required(str)


db.generate_mapping(create_tables=True)
