from dgg_chat.messages import UserJoined, Whisper

from remind_me import remind_me_bot
from models import Session, get_or_create_user


chat = remind_me_bot.chat


@chat.on_user_joined
def on_user_joined(joined: UserJoined):
    with Session() as s:
        user = get_or_create_user(joined.user.nick, s)

        if user.reminder_on_next_join:
            msg = f"Hey {user.nick}! Last time you were here you asked me to remind you of"
            if user.reminder_on_next_join == 'no message':
                msg = f"{msg} something on the next time you joined, but you didn't specify a message."
            else:
                msg = f"{msg} this next time you joined: {user.reminder_on_next_join}"
            chat.send_whisper(user.nick, msg)

            user.reminder_on_next_join = None
            s.commit()


@chat.on_whisper
def on_whisper(whisper: Whisper):
    with Session() as s:
        user = get_or_create_user(whisper.user.nick, s)
        user.has_messaged = True
        s.commit()
