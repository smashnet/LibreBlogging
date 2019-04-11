'''
pagenotfound.py

404 controller.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import cherrypy

from controller.base import BaseController

class PageNotFoundController(BaseController):

  @cherrypy.expose
  def index(self, template_vars=None, status=None, message=None, traceback=None, version=None):
    template_vars = {"bodyclass": "class=main"}
    return self.render_template("404.html", template_vars)
