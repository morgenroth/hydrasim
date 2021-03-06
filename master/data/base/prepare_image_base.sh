#!/bin/bash
#
# This is executed in a chroot inside the mounted image
#
# Image wil be mounted to <setup>/mnt
#
# All files from <setup>/overlay will be copied to the chroot
# All packages from <setup>packages will be installed in chroot
#
# This file is for the base setup, i.e. it will be excuted only ONCE and all
# changes done  by this file are copied to all nodes
#
# DO NOT edit this file. Do have additonal setup code put it in  a
# modify_image_base.sh image in your <setup> directory
#
# Parameter <image file> <setup>
#
# 2010 IBR


IMAGE_FILE=$1
BASE=$2
SETUP=$3

echo "------- Image setup ---------------------------------------------------"

echo "Preparing image $IMAGE_FILE with"
echo "Base: $BASE"
echo "Configuration: $SETUP"

if [ ! -e "$IMAGE_FILE" ]
then
   echo "$0: Can't see image file $1"
   exit -1
fi

if [ ! -d "$BASE" ]
then
   echo "$0: Can not find base directory  $2"
   exit -1
fi

if [ ! -d "$SETUP" ]
then
   echo "$0: Can not find setup directory  $2"
   exit -1
fi


if [ ! -e "$BASE/mnt" ]
then
    mkdir "$BASE/mnt"
fi


# mount the image
bash "$BASE/magicmount.sh" "$IMAGE_FILE" "$BASE/mnt/"


#We need DNS capability in chroot
cp /etc/resolv.conf $BASE/mnt/tmp/resolv.conf

# install packages
echo "Installing packages"
PACKAGES=`cat $BASE/packages.install | grep -v "^#"`

chroot $BASE/mnt /bin/sh -c "mkdir /var/lock"
chroot $BASE/mnt opkg update

for pkg in $PACKAGES
do
    echo "Install $pkg"
    cp "$BASE/packages/$pkg" "$BASE/mnt/"
    chroot $BASE/mnt /bin/sh -c "opkg install /*.ipk && rm /*.ipk"
done

#copy
echo "Copying overlay"
cp -r -f $BASE/overlay/*  "$BASE/mnt/"
cp -r -f $SETUP/overlay/*  "$BASE/mnt/"
cp -v "$SETUP/modify_image_base.sh" "$BASE/mnt/"

#custom setup preparation
echo ">>>>> Custom image setup"
chroot $BASE/mnt /bin/sh /modify_image_base.sh 
echo ">>>>> Custom image setup done."

# remove the setup script
rm "$BASE/mnt/modify_image_base.sh"

# switch to chroot
chroot "$BASE/mnt" /bin/sh <<EOF

# network configuration
/sbin/uci del network.lan.type
/sbin/uci del network.lan.ipaddr
/sbin/uci del network.lan.netmask
/sbin/uci set network.lan.proto=dhcp

# time sync
/sbin/uci del ntpclient.@ntpserver[3]
/sbin/uci del ntpclient.@ntpserver[2]
/sbin/uci del ntpclient.@ntpserver[1]
/sbin/uci set ntpclient.@ntpserver[0].hostname=10.42.0.30

/sbin/uci commit

# change permissions
/bin/chmod 0755 /etc/init.d/hnd

# enable node initrc
/etc/init.d/hnd enable

# close chroot
EOF

# unmount the image
umount  "$BASE/mnt/"

echo "------- Image setup done ------------------------------------------------"
