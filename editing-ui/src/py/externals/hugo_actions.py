import subprocess
from os import listdir
from os.path import isfile, join, basename
from datetime import datetime
import pytz
import markdown

import common

def hugo_create_post(name):
  #TODO: Validate name
  try:
    subprocess.run(["hugo","new", "posts/%s.md" % name], cwd="./hugo-site", shell=False)
  except SubprocessError as e:
    common.logger.error("Could not create new hugo post file: %s" % e)
    return False
  return True

def hugo_append_markdown(md_file_uuid, md_string):
  with open(common.HUGO_POSTS_DIR + "%s.md" % md_file_uuid, "a") as f:
    f.write(md_string)
    f.close()

def get_posts_from_files():
  '''
  This should look like:
  [{"uuid": uuid_string, "date": date_string, "post": post_string}, {...}]
  '''
  files = [join(common.HUGO_POSTS_DIR, f) for f in listdir(common.HUGO_POSTS_DIR) if (isfile(join(common.HUGO_POSTS_DIR, f)) and not f.startswith('.') and f.endswith('.md'))]
  res = []
  tz = pytz.timezone('Europe/Berlin') #TODO: Make this variable and add to "Settings" page
  for current_file in files:
    with open(current_file, 'r') as f:
      the_uuid = basename(current_file).split('.')[0]
      date = "2019-01-01T00:01:00Z"
      post = ""
      head_separators = 0
      for line in f.readlines():

        if len(line) > 1:
          if line.startswith('---'):
            head_separators += 1
            continue
          parts = line.split(' ')
          if parts[0] == "date:":
            date = parts[1].strip()

        if head_separators >= 2:
          post += line

      dt_utc = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
      dt_loc = dt_utc.astimezone(tz)
      res.append({"uuid": the_uuid, "date": dt_loc, "post": markdown.markdown(post.strip(), extensions=['extra'])})
      res.sort(key=lambda post: post['date'], reverse=True)
      f.close()

  return res
