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

The image is not uploaded to S3 immediately.
The user receives the renamed filename.



Activation
----------

The user associates the filename to a document, which is stored in the API.
At that time, an authenticated activation request is sent to this backend and
the file uploaded to S3; in addition, the files are deleted from incoming.
This step ensures the image is associated with an authenticated user.


Cleaning
--------

The files which are too old are cleaned from incoming. A simple cron triggers
this task. There is no need for an input from the API.
