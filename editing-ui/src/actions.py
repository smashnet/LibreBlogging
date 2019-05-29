import subprocess
from os import listdir
from os.path import isfile, join, basename
from datetime import datetime
import logging
import markdown
import pytz

import config

logger = logging.getLogger("LB - Actions")

def hugo_create_post(id):
  #TODO: Validate name
  try:
    subprocess.run(["hugo","new", "posts/%s.md" % id], cwd="./hugo-site", shell=False)
  except subprocess.SubprocessError as e:
    logger.error("Could not create new hugo post file: %s" % e)
    return False
  return True

def hugo_update_post(id, entry_text):
  filename = config.libreblogging['hugo']['postsdir'] + f"{id}.md"
  if not isfile(filename):
    logger.warning(f"Could not update blog post. There is no file {filename}")
    return False
  # Get front matter
  with open(filename, 'r') as f:
    head_separators = 0
    frontmatter = ""
    for line in f.readlines():
      if head_separators >= 2:
        break
      if line.startswith("---"):
        head_separators += 1
      frontmatter += line
    f.close()
  # Write updated file
  with open(filename, 'w') as f:
    f.write(frontmatter)
    f.write(entry_text)
    f.close()
  return True

def hugo_delete_post(id):
  filename = config.libreblogging['hugo']['postsdir'] + f"{id}.md"
  if not isfile(filename):
    logger.warning(f"Could not delete blog post. There is no file {filename}")
    return False
  try:
    subprocess.run(["rm", filename] , shell=False)
  except subprocess.SubprocessError as e:
    logger.error("Could not delete file: %s" % e)
    return False
  return True

def hugo_append_markdown(md_file_uuid, md_string):
  with open(config.libreblogging['hugo']['postsdir'] + "%s.md" % md_file_uuid, "a") as f:
    f.write(md_string)
    f.close()

def parse_post_from_file(filename, returnMarkdown=False):
  with open(filename, 'r') as f:
    the_uuid = basename(filename).split('.')[0]
    date = "2019-01-01T00:01:00Z"
    post = ""
    head_separators = 0
    for line in f.readlines():
      # Search and parse front matter
      if len(line) > 1:
        if line.startswith('---'):
          head_separators += 1
          continue
        parts = line.split(' ')
        if parts[0] == "date:":
          date = parts[1].strip()
      # Append everything after front matter
      if head_separators >= 2:
        post += line

    dt_utc = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    dt_loc = dt_utc.astimezone(pytz.timezone(config.libreblogging['timezone']))

    f.close()

  if returnMarkdown:
    return {"uuid": the_uuid,
           "date": dt_loc,
           "post": post.strip()
           }
  else:
    return {"uuid": the_uuid,
           "date": dt_loc,
           "post": markdown.markdown(post.strip(), extensions=['extra'])
           }

def get_single_post(id, returnMarkdown=False):
  '''
  {"uuid": uuid_string, "date": date_datetime, "post": post_html_string}
  '''
  filename = join(config.libreblogging['hugo']['postsdir'], f"{id}.md")
  logger.info(f"Opening file: {filename}")
  return parse_post_from_file(filename, returnMarkdown)

def get_posts_from_files():
  '''
  This should look like:
  [{"uuid": uuid_string, "date": date_datetime, "post": post_html_string}, {...}]
  '''
  files = [join(config.libreblogging['hugo']['postsdir'], f) for f in listdir(config.libreblogging['hugo']['postsdir']) if (isfile(join(config.libreblogging['hugo']['postsdir'], f)) and not f.startswith('.') and f.endswith('.md'))]
  res = []
  for current_file in files:
    res.append(parse_post_from_file(current_file))
  res.sort(key=lambda post: post['date'], reverse=True)
  return res

def build_and_deploy():
  try:
    subprocess.run(["./build_and_deploy"], cwd="./scripts", shell=False)
  except subprocess.SubprocessError as e:
    logger.error(f"Error during build and deploy: {e}")
    return False
  return True
