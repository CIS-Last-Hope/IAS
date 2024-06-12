import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String, unique=True)
    username = sa.Column(sa.String, unique=True)
    password_hash = sa.Column(sa.String)
    google_auth_secret = sa.Column(sa.String)

    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id = sa.Column(sa.String, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    expires_at = sa.Column(sa.DateTime)

    user = relationship("User", back_populates="sessions")
