import subprocess

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
  with open("./hugo-site/content/posts/%s.md" % md_file_uuid, "a") as f:
    f.write(md_string)
    f.close()
