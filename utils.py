from datetime import datetime, timedelta


def format_datetime(dt: datetime = datetime.utcnow(), fmt='%Y-%m-%d %H:%M:%S', tz=None):
    s = (dt + timedelta(hours=tz or 0)).strftime(fmt)
    if tz is not None:
        return f"{s}UTC{tz:+03d}"
    return s


def pluralize(val, name):
    return f"{val} {name}{'s' if val != 1 else ''}"


def delta_as_str(delta: timedelta):
    s = []
    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = delta.days - years*365 - months*30

    if years:
        s.append(pluralize(years, 'year'))
    if months:
        s.append(pluralize(months, 'month'))
    if days:
        s.append(pluralize(days, 'day'))

    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds - hours*3600 - minutes*60

    if hours:
        s.append(pluralize(hours, 'hour'))
    if minutes:
        s.append(pluralize(minutes, 'minute'))
    if seconds:
        s.append(pluralize(seconds, 'second'))

    if not s:
        raise Exception('null timedelta')

    if len(s) == 1:
        return s[0]

    return f"{', '.join(s[:-1])} and {s[-1]}"
