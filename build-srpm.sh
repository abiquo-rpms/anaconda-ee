CHROOT=abiquo-5.5-x86_64
CHROOT_DIR=/var/lib/mock/$CHROOT/root
MOCK_CMD="/usr/bin/mock --disable-plugin ccache"

rm -rf tmp rpms
mkdir tmp
mkdir -p rpms/SRPMS

$MOCK_CMD --init -r  $CHROOT
$MOCK_CMD -r $CHROOT --copyin anaconda-11.1.2.195.tar.bz2 /builddir/build/SOURCES/
$MOCK_CMD -r $CHROOT --copyin *.patch /builddir/build/SOURCES/
$MOCK_CMD -r $CHROOT --copyin anaconda.spec /root
$MOCK_CMD -r $CHROOT --shell 'rpmbuild -bs --nodeps /root/anaconda.spec'

cp $CHROOT_DIR/builddir/build/SRPMS/*.rpm rpms/SRPMS/
rm -rf tmp
