'''
libreblogging.py

Coming soon!

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import os

import cherrypy

# Import controller
from controller.home import HomeController
from controller.pagenotfound import PageNotFoundController

class LibreBlogging(object):

  def getRoutesDispatcher(self):
    d = cherrypy.dispatch.RoutesDispatcher()

    d.connect('page_index', '/',
              controller=HomeController(),
              action='index',
              conditions=dict(method=['GET']))

    d.connect('get_entry', '/posts/{entry_id}',
              controller=HomeController(),
              action='get_entry',
              conditions=dict(method=['GET']))

    d.connect('post_entry', '/posts',
              controller=HomeController(),
              action='post_entry',
              conditions=dict(method=['POST']))

    d.connect('page_settings', '/settings',
              controller=HomeController(),
              action='coming_soon',
              conditions=dict(method=['GET']))

    d.connect('page_ipfs', '/ipfs',
              controller=HomeController(),
              action='coming_soon',
              conditions=dict(method=['GET']))

    d.connect('empty', '/empty',
              controller=HomeController(),
              action='empty',
              conditions=dict(method=['GET']))

    return d
