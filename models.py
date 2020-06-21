from typing import List
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

from remind_me import remind_me_bot
from utils import format_datetime


Base = declarative_base()
engine = sa.create_engine('sqlite:///remindme.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
SessionScoper = orm.scoped_session(orm.sessionmaker(bind=engine))


class Session:
    def __init__(self):
        self._s = None

    def __enter__(self):
        self.open()
        return self._s

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def add(self, obj):
        self._s.add(obj)

    def delete(self, obj):
        self._s.delete(obj)

    def commit(self):
        self._s.commit()

    def rollback(self):
        self._s.rollback()

    def open(self):
        self._s = SessionScoper()

    def close(self):
        SessionScoper.remove()
        self._s = None

    def query(self, *args):
        return self._s.query(*args)


session = Session()


def get_or_create_user(nick):
    result = session.query(User).filter(User.nick == nick).all()

    if result:
        return result[0]
    
    user = User(nick=nick)
    session.add(user)
    session.commit()

    return user


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    nick = sa.Column(sa.String, nullable=False)
    time_zone = sa.Column(sa.Integer, default=0)
    has_messaged = sa.Column(sa.Boolean, default=False)
    reminder_on_next_join = sa.Column(sa.String)

    reminders = orm.relationship(
        'Reminder', 
        back_populates='user', 
        order_by='Reminder.remind_time.asc()',
    )

    MAX_REMINDERS = 5

    def __repr__(self):
        return f"User(nick='{self.nick}')"


class Reminder(Base):
    __tablename__ = 'reminders'
    id = sa.Column(sa.Integer, primary_key=True)
    note = sa.Column(sa.String)
    time_created = sa.Column(sa.DateTime, nullable=False)
    time_delta = sa.Column(sa.Integer, nullable=False)
    remind_time = sa.Column(sa.DateTime, nullable=False)

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    user = orm.relationship('User', back_populates='reminders')

    def __repr__(self):
        return f"Reminder(user='{self.user.nick}', remind_time='{format_datetime(self.remind_time)}')"


def setup_db():
    Base.metadata.create_all()
    s = Session()
    s.open()
    users: List[User] = s.query(User).all()
    for user in users:
        if user.has_messaged:
            # only do this if you know what you're doing
            remind_me_bot.chat._users_available_to_whisper.add(user.nick)
    s.close()
