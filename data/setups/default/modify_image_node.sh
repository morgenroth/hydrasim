#!/bin/bash
#
# This is executed in a chroot inside the mounted image by prepare_image_base.sh
#
# This file is for the node setup, i.e. it will be excuted once for EVERY
# image
#
# This can be empty
#
# Parameter <IP> <hostname>


echo "Modify node  for $2 ($1)"



echo "Modify node done."