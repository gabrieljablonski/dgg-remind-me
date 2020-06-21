from os import getenv
from dotenv import load_dotenv
from dgg_chat_bot import DGGChatBot
from dgg_chat.logging import setup_logger, INFO, DEBUG


load_dotenv()
setup_logger(INFO)

dgg_auth_token = getenv('DGG_AUTH_TOKEN')

greeting = "Hi {user}! I'm the reminder bot 🤖, I help you remember stuff."
extra = 'More details at github.com/gabrieljablonski/dgg-remind-me.'

remind_me_bot = DGGChatBot(
    dgg_auth_token, 
    greeting=greeting, 
    extra_help=extra
)


# watch out for cirular imports
import bot_handlers
import chat_handlers
from models import setup_db
from reminder_job import ReminderJob


def init():
    setup_db()
    ReminderJob(remind_me_bot).start()
    remind_me_bot.run_forever()
