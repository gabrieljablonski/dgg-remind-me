from os import getenv
from dotenv import load_dotenv
from dgg_chat_bot import DGGChatBot
from dgg_chat.logging import setup_logger, INFO, DEBUG


load_dotenv()
setup_logger(INFO)

dgg_auth_token = getenv('DGG_AUTH_TOKEN')
extra = 'More details at github.com/gabrieljablonski/dgg-remind-me.'

remind_me_bot = DGGChatBot(dgg_auth_token, extra_help=extra)

import chat_handlers
import command_handlers
from models import setup_db
from reminder_job import ReminderJob


def init():
    setup_db()
    ReminderJob(remind_me_bot).start()
    remind_me_bot.run_forever()
