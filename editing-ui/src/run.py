'''
run.py

Entry file of LibreBlogging.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import os, os.path
import sys

import responder
import markdown
import uuid
import datetime

import common
import hugo_actions

api = responder.API(
                  title="LibreBlogging Editing UI",
                  version="0.0.1",
                  description="Web interface to create a static blog",
                  openapi="3.0.2",
                  docs_route="/docs",
                  static_dir="./editing-ui/static",
                  templates_dir="./editing-ui/src/views"
                  )

def render_template(path, template_vars=None):
  template_vars = template_vars if template_vars else {}
  now = datetime.datetime.now()
  template_vars['currentYear'] = now.year
  return api.template(path, vars=template_vars)

@api.route(before_request=True)
async def check_hidden_method(req, resp):
  if req.method == "post":
    data = await req.media()
    try:
      if data['_method'].lower() in ["delete", "put", "patch"]:
        req.method = data['_method']
        print("Changed request method to", data['_method'])
    except KeyError:
      pass
    print(data)

@api.route("", default=True)
def page_not_found(req, resp):
  resp.status_code = api.status_codes.HTTP_404
  resp.html = render_template("404.html")

@api.route("/")
async def index(req, resp):
  template_vars = {}
  # Read markdown files with posts
  template_vars['posts'] = [common.correct_post_datetime_tz(post) for post in hugo_actions.get_posts_from_files()]
  resp.html = render_template("home/index.html", template_vars)

@api.route("/posts")
class NewBlogpostResource:
  async def on_post(self, req, resp):
    data = await req.media()
    try:
      entry_text = data['entry_text']
    except KeyError:
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request", "message": "Content \"entry_text\" not found in POST body."}
      return
    template_vars = {'entry_text': markdown.markdown(entry_text, extensions=['extra'])}
    template_vars['entry_uuid'] = str(uuid.uuid4())
    dt_loc, dt_local_string = common.get_datetime_tuple()
    template_vars['entry_date'] = dt_local_string
    # Create new post file in hugo-site
    hugo_actions.hugo_create_post(template_vars['entry_uuid'])
    # Write content to markdown file
    hugo_actions.hugo_append_markdown(template_vars['entry_uuid'], entry_text)
    resp.html = render_template("home/new_entry_received.html", template_vars)

@api.route("/posts/{id}")
class BlogpostResource:
  async def on_get(self, req, resp, *, id):
    if not common.is_valid_uuid(id):
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request", "message": "Not a valid UUID."}
      return
    #TODO: Return template that shows complete blogpost as single

  async def on_post(self, req, resp, *, id):
    if not common.is_valid_uuid(id):
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request", "message": "Not a valid UUID."}
      return
    #TODO

  async def on_delete(self, req, resp, *, id):
    if not common.is_valid_uuid(id):
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request", "message": "Not a valid UUID."}
      return
    #Delete file of this post
    if hugo_actions.hugo_delete_post(id):
      resp.media = {"status": "200 OK", "message": "Post deleted"}


if __name__ == '__main__':
  api.run()
