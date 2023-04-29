import datetime


def getNow():
    tz = datetime.timezone(datetime.timedelta(hours=-3))
    return datetime.datetime.now(tz=tz)
