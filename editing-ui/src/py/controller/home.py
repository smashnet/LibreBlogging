'''
home.py

Home controller of LibreBlogging.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import cherrypy
import markdown
import uuid
import time
from datetime import datetime
import pytz

from controller.base import BaseController
from externals import hugo_actions
import common

@cherrypy.expose
class HomeController(BaseController):

  def index(self):
    template_vars = {}
    # Read markdown files with posts
    template_vars['posts'] = [common.correct_post_datetime_tz(post) for post in hugo_actions.get_posts_from_files()]
    return self.render_template("home/index.html", template_vars)

  def get_entry(self, entry_id):
    return entry_id

  def post_entry(self, entry_text):
    #TODO: Check entry_text for malicious content (injections, etc... )!
    template_vars = {'entry_text': markdown.markdown(entry_text, extensions=['extra'])}
    template_vars['entry_uuid'] = str(uuid.uuid4())
    ts = int(time.time())
    template_vars['entry_ts'] = ts
    tz = pytz.timezone('Europe/Berlin') #TODO: Make this variable and add to "Settings" page
    dt_utc = datetime.fromtimestamp(ts)
    dt_loc = dt_utc.astimezone(tz)
    template_vars['entry_date'] = dt_loc.strftime('%T - %B %d, %Y, %Z')
    # Create new post file in hugo-site
    hugo_actions.hugo_create_post(template_vars['entry_uuid'])
    # Write content to markdown file
    hugo_actions.hugo_append_markdown(template_vars['entry_uuid'], entry_text)
    return self.render_template("home/new_entry_received.html", template_vars)

  def settings(self):
    template_vars = {}
    return self.render_template("home/settings.html", template_vars)

  def coming_soon(self):
    template_vars = {}
    return self.render_template("home/coming_soon.html", template_vars)

  def empty(self):
    template_vars = {}
    return self.render_template("home/empty.html", template_vars)
