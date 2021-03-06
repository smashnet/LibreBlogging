FROM alpine:3.9
MAINTAINER Nicolas Inden <nicolas@inden.one>

WORKDIR /app

# Install python3
RUN apk add --no-cache python3 python3-dev&& \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

# Install recent Hugo version
ENV HUGO_VERSION=0.70.0
ENV HUGO_TYPE=_extended

ENV HUGO_ID=hugo${HUGO_TYPE}_${HUGO_VERSION}
ADD https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/${HUGO_ID}_Linux-64bit.tar.gz /tmp
RUN tar -xf /tmp/${HUGO_ID}_Linux-64bit.tar.gz -C /tmp \
    && mkdir -p /usr/local/sbin \
    && mv /tmp/hugo /usr/local/sbin/hugo \
    && rm -rf /tmp/${HUGO_ID}_linux_amd64 \
    && rm -rf /tmp/${HUGO_ID}_Linux-64bit.tar.gz \
    && rm -rf /tmp/LICENSE.md \
    && rm -rf /tmp/README.md

# Install recent IPFS version
ENV IPFS_VERSION=0.5.1

ADD https://github.com/ipfs/go-ipfs/releases/download/v${IPFS_VERSION}/go-ipfs_v${IPFS_VERSION}_linux-amd64.tar.gz /tmp
RUN tar -xf /tmp/go-ipfs_v${IPFS_VERSION}_linux-amd64.tar.gz -C /tmp \
    && mkdir -p /usr/local/sbin \
    && mv /tmp/go-ipfs/ipfs /usr/local/sbin/ipfs \
    && rm -rf /tmp/go-ipfs

# Install other needed packages
RUN apk add --no-cache git asciidoctor libc6-compat libstdc++ ca-certificates zlib-dev jpeg-dev build-base nodejs npm ncurses su-exec busybox-suid

COPY requirements.txt ./

# Install python requirements
RUN pip install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Create required paths
ENV CONFIG_PATH /app/config
ENV IPFS_PATH /app/ipfs-data
ENV IPFS_STAGING /app/ipfs-staging
ENV HUGO_SITE /app/hugo-site
ENV POSTS_PATH /app/hugo-site/content/posts
RUN mkdir -p $CONFIG_PATH \
  && mkdir -p $IPFS_PATH \
  && mkdir -p $IPFS_STAGING \
  && mkdir -p $HUGO_SITE \
  && mkdir -p $POSTS_PATH

COPY editing-ui ./editing-ui
COPY hugo-site-template ./hugo-site-template
COPY scripts ./scripts

RUN cd editing-ui && npm install && npm run compile

COPY entrypoint.sh ./

# --------- Editing UI ports
ENV PORT 9000
EXPOSE 9000

# --------- IPFS ports
# Swarm TCP; should be exposed to the public
EXPOSE 4001
# Daemon API; must not be exposed publicly but to client services under you control
EXPOSE 5001
# Web Gateway; can be exposed publicly with a proxy, e.g. as https://ipfs.example.org
EXPOSE 8080
# Swarm Websockets; must be exposed publicly when the node is listening using the websocket transport (/ipX/.../tcp/8081/ws).
EXPOSE 8081

VOLUME ["$CONFIG_PATH"]
VOLUME ["$IPFS_PATH"]
VOLUME ["$HUGO_SITE"]

ENTRYPOINT [ "./entrypoint.sh" ]
