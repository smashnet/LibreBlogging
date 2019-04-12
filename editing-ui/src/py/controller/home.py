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

from controller.base import BaseController

class HomeController(BaseController):

  @cherrypy.expose
  def index(self):
    template_vars = {"bodyclass": "class=main"}
    return self.render_template("home/index.html", template_vars)

  @cherrypy.expose
  def empty(self):
    template_vars = {"bodyclass": "class=main"}
    return self.render_template("home/empty.html", template_vars)
