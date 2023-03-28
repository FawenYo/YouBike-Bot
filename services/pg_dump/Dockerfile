FROM alpine@sha256:e2e16842c9b54d985bf1ef9242a313f36b856181f188de21313820e177002501

RUN apk --no-cache add postgresql-client && apk add --update coreutils && rm -rf /var/cache/apk/*

WORKDIR /app

ADD . /app
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/dump.sh

ENTRYPOINT ["/app/entrypoint.sh"]
