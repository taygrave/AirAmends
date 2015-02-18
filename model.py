from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

engine = create_engine("sqlite:///airdata.db", echo=True)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property

####  INITIALIZING  ####

def create_db():
    """This creates a new db when called"""
    Base.metadata.create_all(engine)

def connect(db="sqlite:///airdata.db"):
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
class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    acess_token = Column(String(64), nullable=False)

    def save(self):
        session.add(self)
        session.commit()

    def save_new_token(self, access_token):
        """Save new access token in the database."""
        session.query(User).filter_by(id=self.id).update({"access_token": access_token})
        session.commit()

    def request_email_ids(self):
        pass

    def __repr__(self):
        return "<User: id=%r, name=%s>" %(self.id, self.name)


class Email(Base):
    __tablename__ = "Emails"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    msg_id = Column(String(64), nullable=False)
    thread_id = Column(String(64), nullable=False)
    body = Column(Text, nullable=False)

    user = relationship("User", backref="emails")

    def __repr__(self):
        return "<Email id=%r, user_id=%d, msg_id=%s>" %(self.id, self.user_id, self.msg_id)

class Flight(Base):
    __tablename__="Flights"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    msg_id = Column(Integer, ForeignKey('Emails.id'), nullable=False)  #can this be the same as a trip id or do we need one of those too?
    date = Column(DateTime, nullable=False)
    depart = Column(String(64), nullable=False)
    arrive = Column(String(64), nullable=False)
    #need these for CO2 calc? not sure yet: flying time / distance

    def __repr__(self):
        return "<Flight: id=%r, user_id=%s, msg_id=%s, date=%r, depart=%s, arrive=%s>" %(self.id, self.user_id, self.msg_id, self.date, self.depart, self.arrive)








