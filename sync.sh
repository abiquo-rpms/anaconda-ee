rsync -rtlz . root@rpm-builder:/home/rpmbuilder/anaconda/
ssh root@rpm-builder "chown rpmbuilder -R /home/rpmbuilder/anaconda/"
