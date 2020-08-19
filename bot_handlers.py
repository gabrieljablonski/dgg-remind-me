from re import findall
from sys import maxsize
from typing import Optional
from datetime import datetime, timedelta
from dgg_chat_bot import Message
from dgg_chat_bot.exceptions import InvalidCommandArgumentsError

from remind_me import remind_me_bot as bot
from models import session, User, Reminder, get_or_create_user
from utils import format_datetime, delta_as_str


@bot.on_command('reminders', 'r', 'list')
def reminders(message: Message):
    """
    "!reminders"
    Lists the reminders you currently have set.
    Use "!delete <n>" to delete one.
    """

    user = get_or_create_user(message.user.nick)

    if not user.reminders:
        return bot.reply("""You don't have any set reminders. Use "!remindme" to set one.""")

    tz = user.time_zone
    msgs = ['Reminders you currently have set:']
    for i, r in enumerate(user.reminders):
        tc = r.time_created
        rt = r.remind_time
        diff = rt-datetime.utcnow()
        td = timedelta(seconds=diff.total_seconds())
        msg = (
            f"{i+1}. ({format_datetime(rt, tz=tz)}) "
            f"Triggers in {delta_as_str(td)}. "
            f"Set on {format_datetime(tc, tz=tz)}. "
            f"Note: {r.note}"
        )
        msgs.append(msg)

    msgs.append('Use "!delete <n>" to delete one.')

    bot.reply_multiline(msgs)


@bot.on_command('delete', 'd', 'remove', optional_args=True)
def delete(n: int = maxsize, message: Message = None):
    """
    "!delete <n>"
    Delete the reminder number <n>, 1 being the closest one, 2 the next, and so on.
    If <n> is not given, does the same as "!reminders".
    """

    if n == maxsize:
        return reminders(message)

    if n <= 0:
        raise InvalidCommandArgumentsError('<n> must be positive')

    user = get_or_create_user(message.user.nick)

    if n > len(user.reminders):
        raise InvalidCommandArgumentsError(
            f"invalid <n>. number of reminders is currently {len(user.reminders)}"
        )

    reminder = user.reminders[n-1]

    session.delete(reminder)
    session.commit()

    bot.reply(f"Successfully deleted reminder #{n}.")


@bot.on_command('nexttime', 'nt', optional_args=True)
def next_time(note, message: Message):
    """
    "!nexttime [<note>]".
    Reminds you of <note> next time you join the chat.
    <note> is optional.
    """

    user = get_or_create_user(message.user.nick)
    user.reminder_on_next_join = note or 'no message.'
    session.commit()

    msg = f"All set! Next time you join I'll remind you"

    if note:
        msg = f"{msg} of '{note}'."
    else:
        msg = f"{msg}."

    bot.reply(msg)


@bot.on_command('timezone', 'tz', optional_args=True)
def time_zone(tz: int = maxsize, message: Message = None):
    """
    "!timezone [<tz>]".
    Sets your time zone to the specified <tz> value.
    <tz> is the offset from UTC, ranging from -12 to 12.
    If <tz> is not provided, retrieves currently set time zone.
    """

    user = get_or_create_user(message.user.nick)

    action = 'is currently'
    if tz != maxsize:
        if tz < -12 or tz > 12:
            raise InvalidCommandArgumentsError(
                '<tz> should be between -12 and 12'
            )
        user.time_zone = tz
        session.commit()
        action = 'was set to'

    local_time = datetime.utcnow() + timedelta(hours=user.time_zone)

    msg = (
        f"Your time zone {action} UTC{user.time_zone:+03d}, so it should be {format_datetime(local_time)} there. "
        f"""If that's incorrect, use "!timezone <tz>" to correct it."""
    )
    return bot.reply(msg)


@bot.on_command('remindme', 'rm', 'add')
def remind_me(expr, note: Optional[str], message: Message):
    """
    "!remindme <expr> [<note>]".
    Reminds you of <note> after the time evaluated from <expr>. <note> is optional.
    <expr> is of format "99y99M99999d99999h99999m99999s", in which "y" is year, 
    "M" is month, etc., and the 9s indicate the field's maximum value. 
    Order is enforced. All fields are optional, but at least one is required.
    """

    user = get_or_create_user(message.user.nick)

    if len(user.reminders) >= user.MAX_REMINDERS:
        raise Exception(
            f'you can have up to {user.MAX_REMINDERS} reminders at a time. use "!delete <n>" to delete one'
        )

    pattern = r'^(?:(\d{1,2})y)?(?:(\d{1,2})M)?(?:(\d{1,5})d)?(?:(\d{1,5})h)?(?:(\d{1,5})m)?(?:(\d{1,5})s)?$'
    match = findall(pattern, expr)

    if not match or not any(match[0]):
        raise InvalidCommandArgumentsError('no match found for <expr>')

    y, mon, d, h, m, s = map(lambda i: int(i or 0), match[0])

    now = datetime.utcfromtimestamp(message.timestamp)
    delta = timedelta(days=d + 365*y + 30*mon, hours=h, minutes=m, seconds=s)
    remind_time = now + delta

    reminder = Reminder(
        user=user,
        note=note or 'no message.',
        time_created=now,
        time_delta=delta.total_seconds(),
        remind_time=remind_time,
    )

    session.add(reminder)
    session.commit()

    bot.reminder_job.check_next_reminder()

    msg = (
        f"All set! In {delta_as_str(delta)} "
        f"(at {format_datetime(remind_time, tz=user.time_zone)}) "
        f"I'll remind you"
    )

    if note:
        msg = f"{msg} of {note}"
    else:
        msg = f"{msg}."

    bot.reply(msg)


@bot.on_command('remindmeon', 'rmo', 'addon')
def remind_me_on(expr, note: Optional[str], message: Message):
    """
    "!remindmeon <expr> [<note>]". 
    Reminds you of <note> after the time evaluated from <expr>. <note> is optional.
    <expr> is of format "YYYY-MM-DD@hh:mm:ss". If only the date is given, 
    the time is set to "00:00:00". If only the time is given, date is set to current day.
    <note> is optional. The expression is evaluated based on your set time zone (use "!timezone" to check).
    """

    user = get_or_create_user(message.user.nick)

    if len(user.reminders) >= user.MAX_REMINDERS:
        raise Exception(
            f'you can have up to {user.MAX_REMINDERS} reminders at a time. use "!delete <n>" to delete one'
        )

    pattern = r'^(?:(\d{4})-(\d\d?)-(\d\d?))?(?:@?(\d\d?):(\d\d?):(\d\d?))?$'
    match = findall(pattern, expr)

    if not match:
        raise InvalidCommandArgumentsError('no match found for <expr>')

    y, mon, d, h, m, s = map(lambda i: int(i or 0), match[0])

    if not y:
        now = datetime.utcnow()
        y, mon, d = now.year, now.month, now.day

    time_zone_diff = timedelta(hours=user.time_zone)
    now = datetime.utcfromtimestamp(message.timestamp)
    remind_time = datetime(
        year=y, month=mon, day=d, 
        hour=h, minute=m, second=s
    ) - time_zone_diff
    delta = remind_time - now

    if (delta_sec := delta.total_seconds()) <= 0:
        raise InvalidCommandArgumentsError(
            "you can't set a reminder to a time that has already passed"
        )

    reminder = Reminder(
        user=user,
        note=note or 'no message.',
        time_created=now,
        time_delta=delta_sec,
        remind_time=remind_time,
    )

    session.add(reminder)
    session.commit()

    bot.reminder_job.check_next_reminder()

    msg = (
        f"All set! In {delta_as_str(delta)} "
        f"(at {format_datetime(remind_time, tz=user.time_zone)}) "
        f"I'll remind you"
    )

    if note:
        msg = f"{msg} of {note}"
    else:
        msg = f"{msg}."

    bot.reply(msg)
