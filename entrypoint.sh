#!/bin/sh

cd /app

# Check if hugo site exists. If not, copy site template.
if [ ! -f "hugo-site/config.toml" ]; then
  echo "No hugo site found. Copying template!"
  mkdir hugo-site
  cp -r hugo-site-template/* hugo-site
fi

# Start editing UI
python3 -u editing-ui/src/run.py
