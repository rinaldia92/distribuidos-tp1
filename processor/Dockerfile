FROM python:3-alpine

RUN apk update \
 && apk add jq \
 && apk add git \
 && rm -rf /var/cache/apk/*

COPY processor /
COPY common /common

ENTRYPOINT ["/bin/sh"]