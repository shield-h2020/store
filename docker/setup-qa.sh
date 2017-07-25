#!/bin/bash

pip3.4 install -r ${CNTR_FOLDER_DEV}/docker/requirements-qa.txt



#
# DO NOT REMOVE THIS - LEAVE IT AS THE LAST LINE IN THE FILE.
# Convey the commands from the command line so the container does what it is intended to do once it is up and running.
exec "$@"
