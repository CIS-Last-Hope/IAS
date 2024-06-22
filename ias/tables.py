import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

from ias.database import engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    email = sa.Column(sa.String, unique=True)
    username = sa.Column(sa.String, unique=True)
    password_hash = sa.Column(sa.String)
    google_auth_secret = sa.Column(sa.String)

    sessions = relationship("Session", back_populates="user")
    courses = relationship("Course", back_populates="creator")
    ratings = relationship("CourseRating", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id = sa.Column(sa.String, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    expires_at = sa.Column(sa.DateTime)

    user = relationship("User", back_populates="sessions")


class Course(Base):
    __tablename__ = 'courses'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, unique=True)
    description = sa.Column(sa.String)
    creator_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    average_rating = sa.Column(sa.Float, default=0.0)

    creator = relationship("User", back_populates="courses")
    materials = relationship("Material", back_populates="course", cascade="all, delete-orphan")
    ratings = relationship("CourseRating", back_populates="course", cascade="all, delete-orphan")


class Material(Base):
    __tablename__ = 'materials'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    filename = sa.Column(sa.String, nullable=False)
    filepath = sa.Column(sa.String, nullable=False)
    course_id = sa.Column(sa.Integer, sa.ForeignKey("courses.id"), nullable=False)

    course = relationship("Course", back_populates="materials")

class CourseRating(Base):
    __tablename__ = 'course_ratings'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    rating = sa.Column(sa.Integer, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    course_id = sa.Column(sa.Integer, sa.ForeignKey("courses.id"), nullable=False)

    user = relationship("User", back_populates="ratings")
    course = relationship("Course", back_populates="ratings")

Base.metadata.create_all(bind=engine)
