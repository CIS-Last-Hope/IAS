import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String, unique=True)
    username = sa.Column(sa.String, unique=True)
    password_hash = sa.Column(sa.String)

class Operations(Base):
    __tablename__ = 'operations'
    id = sa.Column(sa.Integer,primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), index=True)
    date = sa.Column(sa.Date)
    kind = sa.Column(sa.String)
    amount = sa.Column(sa.Numeric(10,2))
    description = sa.Column(sa.String, nullable=True)