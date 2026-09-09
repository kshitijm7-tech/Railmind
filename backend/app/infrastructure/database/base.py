from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert

class Base(DeclarativeBase):
    pass