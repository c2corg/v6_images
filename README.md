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
At that time, a request is sent to S3 to move the thumbnails from the incoming bucket to the public bucket.
This step ensures the image is associated with an authenticated user.


Cleaning
--------

The files which were not activated are automatically expired by S3.


Building and running with Docker
-------------------------------

docker build -t gberaudo/c2corg_images . && docker-compose up
