FROM redis:7.2.7-alpine

COPY /cache/entrypoint.sh /etc/redis/entrypoint.sh

RUN chmod +x /etc/redis/entrypoint.sh

ENTRYPOINT ["sh", "/etc/redis/entrypoint.sh"]
