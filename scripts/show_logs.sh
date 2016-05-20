#!/bin/sh

for i in `docker-compose ps -q`
do
  echo "\033[1mDocker log for $i\033[0m"
  docker logs $i
done
