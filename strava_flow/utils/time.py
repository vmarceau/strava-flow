import datetime
import calendar


def timestamp_from_datetime(timestamp: datetime.datetime) -> float:
    return calendar.timegm(timestamp.timetuple()) + timestamp.microsecond / 1000000


def datetime_from_timestamp(timestamp: float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)