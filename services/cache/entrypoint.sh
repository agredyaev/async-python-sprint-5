#!/bin/bash
set -e
set -x

{
  echo "requirepass $REDIS_PASSWORD"
  echo "aclfile /etc/redis/users.acl"
  echo "save 20 1"
  echo "loglevel warning"
} > /etc/redis/redis.conf

{
  echo "user $REDIS_USER on >$REDIS_PASSWORD ~* &* +@all"

} > /etc/redis/users.acl

chmod 600 /etc/redis/redis.conf
chmod 600 /etc/redis/users.acl

exec redis-server /etc/redis/redis.conf
