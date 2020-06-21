import time
from typing import List
from datetime import datetime, timedelta
from threading import Thread
from sqlalchemy.orm.exc import ObjectDeletedError

from models import Session, session, User, Reminder
from utils import format_datetime, delta_as_str


class ReminderJob:
    def __init__(self, bot):
        self._bot = bot
        self._next_reminder = 0
        self._session = Session()

        self._session.open()
        self.check_next_reminder(self._session)

        setattr(bot, 'reminder_job', self)

    def check_next_reminder(self, s=None):
        if not s:
            s = session

        reminders: List[Reminder] = (
            s.query(Reminder)
             .order_by(Reminder.remind_time.asc())
             .limit(1)
             .all()
        )

        if not reminders:
            self._next_reminder = 0
            return

        self._next_reminder = reminders[0].id

    def _job(self):
        while True:
            time.sleep(1)  # avoid cpu hogging
            now = datetime.utcnow()

            if not self._next_reminder:
                continue

            try:
                r = self._session.query(Reminder).get(self._next_reminder)
                if not r:
                    raise ObjectDeletedError
            except ObjectDeletedError:
                self.check_next_reminder()
                continue

            if now < r.remind_time:
                continue

            tc = r.time_created
            td = timedelta(seconds=r.time_delta)
            rt = r.remind_time
            tz = r.user.time_zone

            nick = r.user.nick
            msg = (
                f"Hi {nick}! On {format_datetime(tc, tz=tz)}, you asked me to remind you "
                f"after {delta_as_str(td)} (on {format_datetime(rt, tz=tz)}) of"
            )

            if r.note != 'no message':
                msg = f"{msg} this: {r.note}"
            else:
                msg = f"{msg} something, but you didn't specify a message."

            self._bot.chat.send_whisper(nick, msg)

            self._session.delete(r)
            self._session.commit()

            self.check_next_reminder(s=self._session)

    def start(self):
        Thread(target=self._job, daemon=True).start()
