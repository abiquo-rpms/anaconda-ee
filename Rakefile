task :updateimg do
  require 'fileutils'
  `dd if=/dev/zero of=/tmp/updates.img bs=1k count=2440`
  `mkfs.ext2 -F /tmp/updates.img`
  `sudo mount -o loop /tmp/updates.img /mnt/`
  Dir['anaconda-ee-11.1.2.242/*.py'].each do |f|
    FileUtils.cp f, '/mnt/'
  end
  Dir['anaconda-ee-11.1.2.242/installclasses/*.py'].each do |f|
    FileUtils.cp f, '/mnt/'
  end
  Dir['anaconda-ee-11.1.2.242/ui/*'].each do |f|
    FileUtils.cp f, '/mnt/'
  end
  Dir['anaconda-ee-11.1.2.242/iw/*'].each do |f|
    FileUtils.cp f, '/mnt/'
  end
  FileUtils.cp_r 'anaconda-ee-11.1.2.242/abiquo_upgrades', '/mnt'
  `sudo sync`
  `sudo umount /mnt/`
  `scp /tmp/updates.img root@mirror:/mirror/updates-dev.img`
end
