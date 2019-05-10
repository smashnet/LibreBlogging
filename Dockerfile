FROM alpine:3.9
MAINTAINER Nicolas Inden <nicolas@inden.one>

WORKDIR /app

# Install python3
RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

# Install recent Hugo version
ENV HUGO_VERSION=0.55.5
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

# Install other needed packages
RUN apk add --no-cache git asciidoctor libc6-compat libstdc++ ca-certificates zlib-dev jpeg-dev build-base nodejs npm ncurses python3-dev

COPY requirements.txt ./

# Install python requirements
RUN pip install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

COPY editing-ui ./editing-ui
COPY hugo-site-template ./hugo-site-template

RUN cd editing-ui && npm install && npm run compile

COPY entrypoint.sh ./

ENV PORT 8080
EXPOSE 8080

VOLUME ["/app/hugo-site"]

ENTRYPOINT [ "./entrypoint.sh" ]
