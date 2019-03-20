import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class DepartmentName(Base):
    __tablename__ = 'departmentname'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="departmentname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class EmployName(Base):
    __tablename__ = 'employname'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    description = Column(String(150))
    salary = Column(String(10))
    feedback = Column(String(250))
    date = Column(DateTime, nullable=False)
    departmentnameid = Column(Integer, ForeignKey('departmentname.id'))
    departmentname = relationship(
        DepartmentName, backref=backref('employname', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="employname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'description': self. description,
            'salary': self. salary,
            'feedback': self. feedback,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///colleges.db')
Base.metadata.create_all(engin)
