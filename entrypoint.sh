#!/bin/sh
set -e
user=libreblogging
repo="$IPFS_PATH"
UID="${UID:-1000}"

if [ `id -u` -eq 0 ]; then
  if ! id -u $user > /dev/null 2>&1; then
    # Create non privileged user with UID from env (default 1000)
    adduser -D -h /app -u $UID -G users $user
    # Set user as owner of /app
    chown -R libreblogging:users /app
  fi
  echo "Changing user to $user"
  # ensure folder is writable
  su-exec "$user" test -w /app || chown -R -- "$user" /app
  # restart script with new privileges
  exec su-exec "$user" "$0" "$@"
fi

# 2nd invocation with regular user
ipfs version

if [ -e "$repo/config" ]; then
  echo "Found IPFS fs-repo at $repo"
else
  case "$IPFS_PROFILE" in
    "") INIT_ARGS="" ;;
    *) INIT_ARGS="--profile=$IPFS_PROFILE" ;;
  esac
  ipfs init $INIT_ARGS
  ipfs config Addresses.API /ip4/0.0.0.0/tcp/5001
  ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080
fi

ipfs daemon --migrate=true --enable-namesys-pubsub &

cd /app

# Check if hugo site exists. If not, copy site template.
if [ ! -f "hugo-site/config.toml" ]; then
  echo "No hugo site found. Copying template!"
  mkdir -p hugo-site
  cp -r hugo-site-template/* hugo-site
fi

# Start editing UI
python3 -u editing-ui/src/run.py
