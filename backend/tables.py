import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

from backend.database import engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    email = sa.Column(sa.String, unique=True)
    username = sa.Column(sa.String, unique=True)
    password_hash = sa.Column(sa.String)
    google_auth_secret = sa.Column(sa.String)

    sessions = relationship("Ses", back_populates="user")
    courses = relationship("Course", back_populates="creator")
    ratings = relationship("CourseRating", back_populates="user")


class Ses(Base):
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
    creator_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    average_rating = sa.Column(sa.Float, default=0.0)

    creator = relationship("User", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    ratings = relationship("CourseRating", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = 'lessons'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    filename = sa.Column(sa.String, nullable=False)
    filepath = sa.Column(sa.String, nullable=False)
    lesson_id = sa.Column(sa.Integer, nullable=False)
    course_id = sa.Column(sa.Integer, sa.ForeignKey("courses.id"), nullable=False)

    course = relationship("Course", back_populates="lessons")


class CourseRating(Base):
    __tablename__ = 'course_ratings'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    rating = sa.Column(sa.Integer, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    course_id = sa.Column(sa.Integer, sa.ForeignKey("courses.id"), nullable=False)

    user = relationship("User", back_populates="ratings")
    course = relationship("Course", back_populates="ratings")


class Admin(Base):
    __tablename__ = 'admins'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    email = sa.Column(sa.String, unique=True)
    username = sa.Column(sa.String, unique=True)
    password_hash = sa.Column(sa.String)


Base.metadata.create_all(engine, checkfirst=True)
admin = User(
    email='admin',
    username='admin',
    password_hash='admin'
)
ses = Ses(
    id='admin',
    user_id=1,
)
Session = sessionmaker(bind=engine)
session = Session()
try:
    session.add(admin)
    session.add(ses)
    session.commit()
except SQLAlchemyError:
    print('admin created')
session.close()

