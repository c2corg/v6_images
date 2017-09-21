#!/bin/sh -e
GIT_HASH=`git rev-parse HEAD`

REPO="c2corg/v6_images"

if [ "$TRAVIS_PULL_REQUEST" != "false" ]; then
  echo "Not building docker images out of Pull Requests"
  exit 0
fi

if [ "$TRAVIS_BRANCH" = "master" ]; then
  DOCKER_IMAGE="${REPO}:latest"
  DOCKER_SOURCE="branch '${TRAVIS_BRANCH}'"
elif [ ! -z "$TRAVIS_TAG" ]; then
  DOCKER_IMAGE="${REPO}:${TRAVIS_TAG}"
  DOCKER_SOURCE="tag '${TRAVIS_TAG}'"
elif [ ! -z "$TRAVIS_BRANCH" ]; then
  DOCKER_IMAGE="${REPO}:${TRAVIS_BRANCH}"
  DOCKER_SOURCE="branch '${TRAVIS_BRANCH}'"
else
  echo "Don't know how to build image"
  exit 1
fi

echo "Building docker image '${DOCKER_IMAGE}' out of ${DOCKER_SOURCE}"
docker build -t "${DOCKER_IMAGE}" --build-arg "GIT_HASH=${GIT_HASH}" .
docker inspect "${DOCKER_IMAGE}"
docker history "${DOCKER_IMAGE}"
