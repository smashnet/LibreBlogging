'''
common.py

Holds severals functions commonly used in LibreBlogging.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import json
import logging
import os, os.path
import time
from datetime import datetime
import pytz
import uuid

NAME = "editing-ui"
VERSION = "0.0.1"
DATA_DIR = os.path.abspath(os.getcwd()) + "/%s-data/" % NAME
DB_STRING = DATA_DIR + "database.db"

# Further service dependent configuration:
PHOTO_DIR = DATA_DIR + "img/"
PHOTO_THUMBS_DIR = DATA_DIR + "thumbs/"
VIEWS_PATH = os.path.abspath(os.getcwd()) + "/editing-ui/src/views"
try:
  PUBLIC_URL = os.environ['VIRTUAL_HOST']
except KeyError:
  PUBLIC_URL = "localhost"

HUGO_DIR = "./hugo-site/"
HUGO_POSTS_DIR = HUGO_DIR + "content/posts/"
HUGO_CONFIG_FILE = f"{HUGO_DIR}/config.toml"
hugo_config = {}

IPFS_DIR = "./ipfs-data/"
ipfs_config = {}

DATE_FORMAT = "%B %d, %Y - %T %Z"
TIMEZONE = pytz.timezone('Europe/Berlin')

logger = logging.getLogger("LibreBlogging")

def get_datetime_tuple():
  ts = int(time.time())
  dt_utc = datetime.fromtimestamp(ts)
  dt_loc = dt_utc.astimezone(TIMEZONE)
  return dt_loc, dt_loc.strftime(DATE_FORMAT)

def correct_post_datetime_tz(post):
  post['date'] = post['date'].strftime(DATE_FORMAT)
  return post

def is_valid_uuid(id):
  try:
    uuid.UUID(id, version=4)
  except ValueError:
    return False
  return True

def DBtoDict(res):
  descs = [desc[0] for desc in res.description]
  item = res.fetchone()
  if item == None:
    return {}
  else:
    return dict(zip(descs, item))

def DBtoList(res):
  descs = [desc[0] for desc in res.description]
  intermediate = res.fetchall()
  return [dict(zip(descs, item)) for item in intermediate]
