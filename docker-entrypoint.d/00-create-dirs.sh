#!/bin/sh

set -e

for folder in "${TEMP_FOLDER}" "${INCOMING_FOLDER}" "${ACTIVE_FOLDER}"; do
  mkdir -p "${folder}"
done
