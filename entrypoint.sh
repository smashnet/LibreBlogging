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

if [[ -z "$NO_IPFS" ]]; then
  # NO_IPFS is not set, so we start IPFS
  ipfs daemon --migrate=true --enable-namesys-pubsub &
elif [[ "$NO_IPFS" = "false" ]]; then
  ipfs daemon --migrate=true --enable-namesys-pubsub &
elif [[ "$NO_IPFS" = "true" ]]; then
  echo "NO_IPFS is set to -true-. Not starting IPFS..."
fi

cd /app

# If we have the Dockerfile in /app we probably bound ./ to /app and are in development as Dockerfile is not part of the production image.
# In this case do npm stuff
if [ -f "Dockerfile" ]; then
  ./scripts/dev_post_start_commands
fi

# Register cron job to refresh IPNS record every 8 hours
echo "0 0,8,16 * * * /app/scripts/refresh_ipns" | crontab - && crond -f &

# Check if hugo site exists. If not, copy site template.
if [ ! -f "hugo-site/config.toml" ]; then
  echo "No hugo site found. Copying template!"
  mkdir -p hugo-site
  mkdir -p hugo-site/content/posts
  cp -r hugo-site-template/* hugo-site
fi

# Start editing UI
python3 -u editing-ui/src/run.py &

# Start blog preview
cd /app/hugo-site/public
python3 -m http.server
