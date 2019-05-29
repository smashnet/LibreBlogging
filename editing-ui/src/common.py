'''
common.py

Holds severals functions commonly used in LibreBlogging.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import logging
import time
from datetime import datetime
import uuid
import pytz

import config

logger = logging.getLogger("LibreBlogging")

def get_datetime_tuple():
  ts = int(time.time())
  dt_utc = datetime.fromtimestamp(ts)
  dt_loc = dt_utc.astimezone(pytz.timezone(config.libreblogging['timezone']))
  return dt_loc, dt_loc.strftime(config.libreblogging['date_format'])

def correct_post_datetime_tz(post):
  post['date'] = post['date'].strftime(config.libreblogging['date_format'])
  return post

def is_valid_uuid(id):
  try:
    uuid.UUID(id, version=4)
  except ValueError:
    return False
  return True
