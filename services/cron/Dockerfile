FROM alpine@sha256:e2e16842c9b54d985bf1ef9242a313f36b856181f188de21313820e177002501

RUN apk --no-cache add curl

WORKDIR /app

ADD ./start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]
