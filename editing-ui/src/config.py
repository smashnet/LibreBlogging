'''
config.py

Holds severals datastructures for configs of Editing UI, Hugo and IPFS

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import json
import toml
import logging
import os, os.path

logger = logging.getLogger("LibreBlogging")
configfile = "config/libreblogging.json"

# Prepare LibreBlogging config
logger.info("Reading LibreBlogging config file")
try:
  os.mkdir(configfile.split('/')[0])
except FileExistsError as e:
  logger.info("Config directory is already there.")

libreblogging = {}

if os.path.isfile(configfile):
  # Config file exists, read it!
  try:
    with open(configfile, 'r') as cfile:
      libreblogging = json.load(cfile)
  except:
    logger.warning(f"Error reading config file: {configfile}")
else:
  # Config file does not exist. Create it and fill with defaults!
  libreblogging = {
    "name": "LibreBlogging",
    "version": "0.0.1",
    "description": "Web interface to create a static blog",
    "date_format": "%B %d, %Y - %T %Z",
    "timezone": "Europe/Berlin",
    "env": {
      "VIRTUAL_HOST": "localhost"
    },
    "hugo": {
      "basedir": "hugo-site/",
      "postsdir": "hugo-site/content/posts/",
      "configfile": "hugo-site/config.toml"
    },
    "ipfs": {
      "basedir": "ipfs-data/",
      "configfile": "ipfs-data/config"
    }
  }
  with open(configfile, 'w') as cfile:
    json.dump(libreblogging, cfile)

try:
  libreblogging['env']['VIRTUAL_HOST'] = os.environ['VIRTUAL_HOST']
except KeyError:
  libreblogging['env'] = {}
  libreblogging['env']['VIRTUAL_HOST'] = "localhost"

# Read hugo config
logger.info("Reading hugo config file")
hugo = {}
try:
  hugo = toml.load(libreblogging['hugo']['configfile'])
except:
  logger.warning("Error loading hugo config file. Is it there?")
# If params section does not exist, create it
try:
  x = hugo['params']
except KeyError:
  hugo['params'] = {}

# Read IPFS config
ipfs = {}
logger.info("Reading IPFS config file")
try:
  with open(libreblogging['ipfs']['configfile'], 'r') as f:
    ipfs = json.load(f)
except:
  logger.warning("Error loading IPFS config file. Is it there?")
