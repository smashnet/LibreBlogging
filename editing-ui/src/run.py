'''
run.py

Entry file of LibreBlogging.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import subprocess
import logging

import responder
import markdown
import uuid
import datetime
import toml

import config
import common
import actions

logger = logging.getLogger("LB - Responder")

api = responder.API(
                  title=config.libreblogging['name'],
                  version=config.libreblogging['version'],
                  description=config.libreblogging['description'],
                  openapi="3.0.2",
                  docs_route="/docs",
                  static_dir="./editing-ui/static",
                  templates_dir="./editing-ui/src/views"
                  )

@api.on_event('startup')
async def do_startup_stuff():
  return

@api.on_event('shutdown')
async def do_cleanup_stuff():
  return

def render_template(path, template_vars=None):
  template_vars = template_vars if template_vars else {}
  now = datetime.datetime.now()
  template_vars['currentYear'] = now.year
  return api.template(path, vars=template_vars)

@api.route("/error", default=True)
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
        logger.info("Found hidden _method field. Handling POST as %s" % data['_method'])
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
    template_vars['blog_title'] = config.hugo['title']
    try:
      template_vars['blog_description'] = config.hugo['params']['description']
    except KeyError:
      logger.warning("No blog description in config.toml")
      pass
    template_vars['blog_baseurl'] = config.hugo['baseURL']
    resp.html = render_template("home/settings.html", template_vars)

  async def on_put(self, req, resp):
    data = await req.media()
    try:
      config.hugo['title'] = data['title-input']
      config.hugo['params']['description'] = data['description-input']
      config.hugo['baseURL'] = data['baseurl-input']
    except KeyError as e:
      resp.status_code = api.status_codes.HTTP_400
      resp.media = {"status": "400 Bad Request",
                    "message": f"Required field missing: {e}",
                    "required": ["title-input", "description-input", "baseurl-input"]}
      return
    try:
      toml.dump(config.hugo, open(config.libreblogging['hugo']['configfile'], 'w'))
    except:
      await self.on_get(req, resp, alert={"category": "alert-warning", "message": "Could not change settings!", "icon": '<i class="fas fa-exclamation-triangle"></i>'})
      return
    await self.on_get(req, resp, alert={"category": "alert-success", "message": "Successfully changed settings!", "icon": '<i class="fas fa-edit"></i>'})

  async def on_post(self, req, resp):
    data = await req.media()
    try:
      if data['_method'].lower() in ["put"]:
        logger.info("Found hidden _method field. Handling POST as %s" % data['_method'])
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
    template_vars['ipns_full_address'] = f"https://ipfs.io/ipns/{config.ipfs['Identity']['PeerID']}"
  except KeyError:
    logger.warning("No IPFS config found.")
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
    #api.redirect(resp, "/", status_code=307)
    await index(req, resp, alert={"category": "alert-success", "message": "Deployment started... Note, that changes may take a while until visible on your blog!", "icon": '<i class="fas fa-coffee"></i>'})

@api.route("/preview")
async def show_preview(req, resp):
  subprocess.run(["hugo"], cwd="./hugo-site", shell=False)
  api.redirect(resp, f"http://{config.libreblogging['env']['VIRTUAL_HOST']}:9001", status_code=307)

if __name__ == '__main__':
  api.run()
