Image backend service
---------------------

This project handles receiving images from the user and generating smaller
versions. It is using docker to be able to run it either together with the
API machine or on a separate machine.


Upload
--------

The original image uploaded by the user is:
- optionally rotate the image according to the EXIF orientation value
- uniquely renamed using a timestamp and random number;
- stored locally in an "incoming" directory;
- converted to smaller sizes.

The image is uploaded immediately to S3.
The user receives the renamed filename.


Activation
----------

The user associates the filename to a document, which is stored in the API.
At that time, a request is sent to image backend to move original and resized
images from the incoming bucket to the public bucket. This step ensures the
image is associated with an authenticated user.

Configuration
-------------

Configuration should be set by environment variables:

``STORAGE_BACKEND``: (required) ``s3`` or ``local``

* ``s3``: requires ``INCOMING_FOLDER`` and ``ACTIVE_FOLDER``, should be used in
  production.
* ``local``: requires ``INCOMING_BUCKET`` and ``ACTIVE_BUCKET``, should be used
  for tests and development.

``TEMP_FOLDER``: (required) Local folder to store images temporarily.

``INCOMING_FOLDER``: Local folder for incoming files.

``ACTIVE_FOLDER``: Local folder for active files.

``INCOMING_BUCKET``: Name bucket for incoming files.

``INCOMING_PREFIX``: Prefix of the incoming bucket connection options.

``ACTIVE_BUCKET``: Name bucket for active files.

``ACTIVE_PREFIX``: Prefix of the active bucket connection options.

*PREFIX_*``ENDPOINT``: Endpoint url for corresponding prefix.

*PREFIX_*``ACCESS_KEY_ID``: API key for corresponding prefix.

*PREFIX_*``SECRET_KEY``: Secret key for corresponding prefix.

``S3_SIGNATURE_VERSION``: S3 signature version ('s3' or 's3v4'), see [docs](https://botocore.readthedocs.io/en/stable/reference/config.html#botocore.config.Config).

``API_SECRET_KEY``: API secret key, needed to publish images on the active
bucket.

``V5_DATABASE_URL``: Address of the V5 database for the migration script.

``ROUTE_PREFIX``: Path prefix for serving the photo backend API.

``RESIZING_CONFIG``: Configuration of the thumbnail names and sizes serialized in JSON. See c2corg\_images/__init__.py for a description of the format.

``AUTO_ORIENT_ORIGINAL``: `1` to rotate the uploaded image according to the EXIF orientation. Default is `0`.

``CACHE_CONTROL``: Cache-Control value to be set to all the images uploaded to s3. Default is `public, max-age=3600`.

Here is an example configuration with S3 backend on exoscale:

```
STORAGE_BACKEND: s3

TEMP_FOLDER: /srv/images/temp
INCOMING_FOLDER:
ACTIVE_FOLDER:

INCOMING_BUCKET: c2corg_demov6_incoming
INCOMING_PREFIX: EXO
ACTIVE_BUCKET: c2corg_demov6_active
ACTIVE_PREFIX: EXO
EXO_ENDPOINT: https://sos.exo.io
EXO_ACCESS_KEY_ID: xxx
EXO_SECRET_KEY: xxx

API_SECRET_KEY: xxx

V5_DATABASE_URL: postgresql://www-data:www-data@postgres/c2corg
```

Cleaning
--------

The files which were not activated are automatically expired by S3.


Building and running with Docker
-------------------------------

`make run`


Launch images migration from V5 to V6
-------------------------------------

The migration retrieves a list of images from the v5 database. The connection
to the database can be defined as environment variable, for example:

```
V5_DATABASE_URL: postgresql://www-data:www-data@postgres/c2corg
```

The migration script iterates through v5 images. For each *original* image
found:
* If the image already exists in publication bucket, nothing is done (only
  migrate the new ones).
* If the image does not exists in the v6 bucket:
   * the *original* image is copied locally,
   * *resized* images are produced according to configuration,
   * *original* and *resized* images are pushed on publication bucket.

To run the migration script:

``docker-compose exec images migrate``

``docker-compose exec images migrate --help`` to get options list.


Generate *resized* images after migration
-----------------------------------------

This can be used to change the size or quality of *resized* images.

This script iterates through *published* images. For each *original* image
found:
* the *original* image is copied locally,
* *resized* images are produced according to configuration,
* *resized* images are pushed in publication bucket, overwriting old ones.

To regenerate the *resized* images:

``docker-compose exec images resize``

``docker-compose exec images resize --help`` to get options list.


Release on docker hub
---------------------

The project is built by Jenkins.

To make a release:

* Commit and push to master.
* Tag the GIT commit.
* Rebase the `release_${MAJOR_VERSION}` branch to this commit and push the `release_${MAJOR_VERSION}` and
  the tag to github. Make sure to do that at the same time so that Jenkins can see the tag when it builds
  the branch.

To have the int/prod tag point to another version:

* Fast forward or reset the `release_int` or `release_prod` branch to the wanted version.
* Push the branch to github.

We need the `release_*` branches, so that Jenkins can build a new docker image for the major
versions every nights.
