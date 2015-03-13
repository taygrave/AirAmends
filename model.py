from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, distinct, update
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, Float, desc, asc
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

from flask.ext.login import UserMixin

import seed_airports

engine = create_engine("sqlite:///airdata.db", echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

####  INITIALIZING  ####

def create_db():
    """This creates a new db when called"""
    Base.metadata.create_all(engine)
    s = connect()
    seed_airports.seed_airports(s)
    print "Finished created new database, airports table loaded."

def connect(db="sqlite:///airdata.db"):
    """Establishes useable connection to db"""
    global engine
    global session
    engine = create_engine(db, echo=False) 
    session = scoped_session(sessionmaker(bind=engine,
                             autocommit = False,
                             autoflush = False))
    # Returning session for loading it elsewhere
    return session

#### BUILDING THE DATABASE ####

#Table to store each individual user and their authorization creds
class User(UserMixin, Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    email = Column(String(128), nullable=False)
    access_token = Column(String(255), nullable=False)

    def __init__(self, email, access_token):
        self.email = email
        self.access_token = access_token

    def save(self):
        session.add(self)
        session.commit()

    def __repr__(self):
        return "<User: id=%r, email=%s>" %(self.id, self.email)

class Email(Base):
    __tablename__ = "Emails"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    msg_id = Column(String(64), nullable=False)
    date = Column(Date, nullable=False)
    sender = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    body = Column(Text, nullable=False)

    user = relationship("User", backref="emails")

    def __repr__(self):
        return "<Email id=%r, user_id=%d, msg_id=%s>" %(self.id, self.user_id, self.msg_id)

class Flight(Base):
    __tablename__="Flights"

    id = Column(Integer, primary_key=True) #leg id
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    email_id = Column(Integer, ForeignKey('Emails.id'), nullable=False) 
    date = Column(Date, nullable=False)
    depart = Column(String(3), ForeignKey("Airports.id"), nullable=False)
    arrive = Column(String(3), ForeignKey("Airports.id"), nullable=False)

    user = relationship("User", backref="flights")
    email = relationship("Email", backref="flights")
    departure = relationship("Airport", foreign_keys="Flight.depart")
    arrival = relationship("Airport", foreign_keys="Flight.arrive")

    def __repr__(self):
        return "<Flight: id=%r, user_id=%s, email_id=%s, date=%r, depart=%s, arrive=%s>" %(self.id, self.user_id, self.email_id, self.date, self.depart, self.arrive)

class Airport(Base):
    __tablename__="Airports"

    id = Column(String(3), primary_key=True)
    name = Column(String(64), nullable=False)
    city = Column(String(64), nullable=False)
    country = Column(String(64), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    def __repr__(self):
        return "<Airport: id=%r, city=%s>" %(self.id, self.city.encode('utf-8'))

