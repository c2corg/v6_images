Image backend service
---------------------

This project handles receiving images from the user and generating smaller
versions. It is using docker to be able to run it either together with the
API machine or on a separate machine.


Upload
--------

The original image uploaded by the user is:
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


Cleaning
--------

The files which were not activated are automatically expired by S3.


Building and running with Docker
-------------------------------

`make run`


Launch images migration from V5 to V6
-------------------------------------

Migration take source images from v5 S3 read-only bucket, which could be
defined by environment variables, example:

```
V5_BUCKET=c2corg_images_master
V5_ENDPOINT=https://sos.exo.io
V5_PREFIX: EXO
EXO_ACCESS_KEY_ID: ...
EXO_SECRET_KEY: ...
```

Note that here, ``PREFIX`` point out the keys to use as we can have multiple
endpoints (AWS, Exoscale) with different keys.

The migration script iterate through v5 images. For each *original* image found:
* If the image already exists on publication bucket, nothing is done (only
  migrate the new ones).
* If the image do not exists on the v6 bucket:
   * the *original* image is copied locally,
   * *resized* images are produced according to configuration,
   * *original* and *resized* images are pushed on publication bucket.

To run the migration script:

``docker-compose exec images migrate [-v]``


Generate *resized* images after migration
-----------------------------------------

This can be used to change the size or quality of *resized* images.

This script iterate through *published* images. For each *original* image
found:
* the *original* image is copied locally,
* *resized* images are produced according to configuration,
* *resized* images are pushed on publication bucket, overwriting old ones.

To regenerate the *resized* images:

``docker-compose exec images resize_images [-v]``
