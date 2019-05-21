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
import toml

import common
import actions

api = responder.API(
                  title="LibreBlogging Editing UI",
                  version="0.0.1",
                  description="Web interface to create a static blog",
                  openapi="3.0.2",
                  docs_route="/docs",
                  static_dir="./editing-ui/static",
                  templates_dir="./editing-ui/src/views"
                  )

@api.on_event('startup')
async def do_startup_stuff():
  # Read current hugo configuration
  common.hugo_config = toml.load(common.HUGO_CONFIG_FILE)

@api.on_event('shutdown')
async def do_cleanup_stuff():
  return

def render_template(path, template_vars=None):
  template_vars = template_vars if template_vars else {}
  now = datetime.datetime.now()
  template_vars['currentYear'] = now.year
  return api.template(path, vars=template_vars)

@api.on_event('startup')
async def read_config():
  common.logger.info("Reading IPFS config file")
  common.ipfs_config = actions.get_ipfs_config()

@api.route("", default=True)
def page_not_found(req, resp):
  resp.status_code = api.status_codes.HTTP_404
  resp.html = render_template("404.html")

@api.route("/")
async def index(req, resp, alert=None):
  template_vars = {}
  template_vars['url_path'] = "/"
  # Read markdown files with posts
  template_vars['posts'] = [common.correct_post_datetime_tz(post) for post in actions.get_posts_from_files()]
  template_vars['allow_deploy'] = True
  if alert is not None:
    template_vars['alert'] = alert
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
    actions.hugo_create_post(template_vars['entry_uuid'])
    # Write content to markdown file
    actions.hugo_append_markdown(template_vars['entry_uuid'], entry_text)
    resp.status_code = api.status_codes.HTTP_201
    await index(req, resp, alert={"category": "alert-success", "message": "New blog post created!"})

@api.route("/posts/{id}")
class BlogpostResource:
  async def on_get(self, req, resp, *, id):
    if not common.is_valid_uuid(id):
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request", "message": "Not a valid UUID."}
      return
    #TODO: Return template that shows complete blogpost as single
    template_vars = {}
    template_vars['url_path'] = "/posts"

  async def on_post(self, req, resp, *, id):
    data = await req.media()
    try:
      if data['_method'].lower() in ["delete", "put", "patch"]:
        common.logging.info("Found hidden _method field. Handling POST as %s" % data['_method'])
        if data['_method'].lower() == "delete":
          await self.on_delete(req, resp, id=id)
          return
        elif data['_method'].lower() == "put":
          await self.on_put(req, resp, id=id)
          return
    except KeyError:
      pass
    resp.status_code = api.status_codes.HTTP_400
    resp.media = {"status": "400 Bad Request", "message": "POST on given UUID is not allowed"}

  async def on_put(self, req, resp, *, id):
    if not common.is_valid_uuid(id):
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request", "message": "Not a valid UUID."}
      return
    data = await req.media()
    try:
      entry_text = data['entry_text']
    except KeyError:
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request", "message": "Content \"entry_text\" not found in body."}
      return
    if actions.hugo_update_post(id, entry_text):
      await index(req, resp, alert={"category": "alert-success", "message": "Blog post successfully updated!", "icon": '<i class="fas fa-edit"></i>'})
    else:
      await index(req, resp, alert={"category": "alert-warning", "message": "Could not update blog post!", "icon": '<i class="fas fa-exclamation-triangle"></i>'})

  async def on_delete(self, req, resp, *, id):
    if not common.is_valid_uuid(id):
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request", "message": "Not a valid UUID."}
      return
    #Delete file of this post
    if actions.hugo_delete_post(id):
      await index(req, resp, alert={"category": "alert-success", "message": "Blog post successfully deleted!", "icon": '<i class="fas fa-trash"></i>'})
    else:
      await index(req, resp, alert={"category": "alert-warning", "message": "Could not delete blog post!", "icon": '<i class="fas fa-exclamation-triangle"></i>'})

@api.route("/posts/{id}/edit")
class EditBlogpost:
  async def on_get(self, req, resp, *, id):
    if not common.is_valid_uuid(id):
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request", "message": "Not a valid UUID."}
      return
    post = actions.get_single_post(id, returnMarkdown=True)
    post = common.correct_post_datetime_tz(post)
    post['url_path'] = "/posts"
    resp.html = render_template("home/edit_post.html", post)

@api.route("/settings")
class Settings:
  async def on_get(self, req, resp, alert=None):
    template_vars = {}
    template_vars['url_path'] = "/settings"
    if alert is not None:
      template_vars['alert'] = alert
    template_vars['blog_title'] = common.hugo_config['title']
    try:
      template_vars['blog_description'] = common.hugo_config['params']['description']
    except KeyError:
      common.logging.warning("No blog description in config.toml")
      pass
    template_vars['blog_baseurl'] = common.hugo_config['baseURL']
    resp.html = render_template("home/settings.html", template_vars)

  async def on_put(self, req, resp):
    data = await req.media()
    try:
      common.hugo_config['title'] = data['title-input']
      common.hugo_config['params']['description'] = data['description-input']
      common.hugo_config['baseURL'] = data['baseurl-input']
    except KeyError:
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request",
                    "message": "Required field missing.",
                    "required": ["title-input", "description-input", "baseurl-input"]}
      return
    try:
      toml.dump(common.hugo_config, open(common.HUGO_CONFIG_FILE, 'w'))
    except:
      await self.on_get(req, resp, alert={"category": "alert-warning", "message": "Could not change settings!", "icon": '<i class="fas fa-exclamation-triangle"></i>'})
      return
    await self.on_get(req, resp, alert={"category": "alert-success", "message": "Successfully changed settings!", "icon": '<i class="fas fa-edit"></i>'})

  async def on_post(self, req, resp):
    data = await req.media()
    try:
      if data['_method'].lower() in ["put"]:
        common.logging.info("Found hidden _method field. Handling POST as %s" % data['_method'])
        if data['_method'].lower() == "put":
          await self.on_put(req, resp)
          return
    except KeyError:
      pass
    resp.status_code = api.status_codes.HTTP_400
    resp.media = {"status": "400 Bad Request", "message": "No _method field found. (Hint: PUT is allowed)"}

@api.route("/ipfs")
async def ipfs_status(req, resp):
  template_vars = {}
  template_vars['url_path'] = "/ipfs"
  try:
    template_vars['ipns_full_address'] = f"https://ipfs.io/ipns/{common.ipfs_config['Identity']['PeerID']}"
  except KeyError:
    common.logging.warning("No IPFS config found.")
    template_vars['ipns_full_address'] = "No IPFS config"
  resp.html = render_template("home/ipfs_status.html", template_vars)

@api.route("/deploy")
class Deployment:
  async def on_get(self, req, resp):
    resp.html = render_template("home/coming_soon.html")

  async def on_post(self, req, resp):
    @api.background.task
    def build_and_deploy():
      actions.build_and_deploy()

    build_and_deploy()
    api.redirect(resp, "/", status_code=307)

if __name__ == '__main__':
  api.run()
