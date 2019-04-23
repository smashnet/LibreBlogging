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

from controller.base import BaseController

@cherrypy.expose
class HomeController(BaseController):

  def index(self):
    template_vars = {}
    return self.render_template("home/index.html", template_vars)

  def get_entry(self, entry_id):
    return entry_id

  def post_entry(self, entry_text):
    #TODO: Check entry_text for malicious content (injections, etc... )!
    template_vars = {"entry_text": markdown.markdown(entry_text)}
    template_vars["entry_uuid"] = str(uuid.uuid4())
    ts = int(time.time())
    template_vars["entry_ts"] = ts
    template_vars["entry_date"] = datetime.utcfromtimestamp(ts).strftime('%T - %B %d, %Y')
    #TODO: Write content to markdown file
    #TODO: Start process to generate static content for IPFS deployment
    return self.render_template("home/new_entry_posted.html", template_vars)

  def coming_soon(self):
    template_vars = {}
    return self.render_template("home/coming_soon.html", template_vars)

  def empty(self):
    template_vars = {}
    return self.render_template("home/empty.html", template_vars)
