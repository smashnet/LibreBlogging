#!/bin/bash

# Only create container if no container with this name is already there
if [ ! "$(docker ps -q -f name=libreblogging-dev)" ]; then
  docker run --rm -d --name libreblogging-dev -p 8081:8080 -v $(pwd):/app -w /app libreblogging-dev-img
fi

# Install node modules if they are not already there
if [ ! -d "node_modules" ]; then
  docker exec -ti -w /app/editing-ui libreblogging-dev npm install
  docker exec -it -w /app/editing-ui/node_modules/tabler-ui/ libreblogging-dev npm install
fi

# npm start
docker exec -ti -w /app/editing-ui libreblogging-dev npm start
