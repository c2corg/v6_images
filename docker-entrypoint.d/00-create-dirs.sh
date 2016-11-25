#!/bin/sh

for folder in "${TEMP_FOLDER}" "${INCOMING_FOLDER}" "${ACTIVE_FOLDER}"; do
  test -n "${folder}" || exit 1
  mkdir -p "${folder}" || exit 1
  chown www-data:www-data "${folder}" || exit 1
done
