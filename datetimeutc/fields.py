import datetime

try:
    USE_DATEUTIL = False
    import zoneinfo
except ImportError:
    from dateutil import tz
    USE_DATEUTIL = True

from django.contrib.postgres.fields.ranges import ContinuousRangeField
from django.contrib.postgres.forms import DateTimeRangeField
from django.db import models
from django.db.backends.postgresql.psycopg_any import DateTimeRange
from django.utils import timezone
from django.conf import settings


class DateTimeUTCField(models.DateTimeField):
    """Create a DB timestamp field that is TZ naive."""

    description = "Date (with time and no time zone)"

    def __init__(self, *args, **kwargs):
        super(DateTimeUTCField, self).__init__(*args, **kwargs)
        if USE_DATEUTIL:
            self.utc_zoneinfo = tz.gettz('UTC')
        else:
            self.utc_zoneinfo = zoneinfo.ZoneInfo('UTC')

    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
            return 'datetime'
        else:
            return 'timestamp'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        if isinstance(value, datetime.datetime):
            if settings.USE_TZ and timezone.is_naive(value):
                return value.replace(tzinfo=self.utc_zoneinfo)
            return value
        return super(DateTimeUTCField, self).to_python(value)

    def get_prep_value(self, value):
        if isinstance(value, datetime.datetime):
            return value.astimezone(self.utc_zoneinfo)
        return value


class DateTimeRangeUTCField(DateTimeRangeField):
    range_type = DateTimeRange


class DateTimeUTCRangeField(ContinuousRangeField):
    base_field = DateTimeUTCField
    range_type = DateTimeRange
    form_field = DateTimeRangeUTCField

    def db_type(self, connection):
        return "tsrange"
