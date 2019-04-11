'''
run.py

Main file of LibreBlogging.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import os, os.path
import sys

import cherrypy

import config
from libreblogging import LibreBlogging
from controller.pagenotfound import PageNotFoundController

def init_service():
  ## Nothing todo currently
  return

def cleanup():
  ## TODO:
  return

if __name__ == '__main__':
  app = LibreBlogging()
  c = PageNotFoundController()

  conf = {
      '/': {
          'tools.sessions.on': False,
          'request.dispatch': app.getRoutesDispatcher(),
          'tools.staticdir.root': os.path.abspath(os.getcwd()),
          'error_page.404': c.index
      },
      '/static': {
          'tools.staticdir.on': True,
          'tools.staticdir.dir': 'editing-ui/static'
      }
  }

  cherrypy.server.socket_host = '0.0.0.0'
  cherrypy.server.socket_port = 8080

  cherrypy.engine.subscribe('start', init_service)
  cherrypy.engine.subscribe('stop', cleanup)

  cherrypy.quickstart(None, '/', conf)
