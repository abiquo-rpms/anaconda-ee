require 'rake/rpm-utils'
task :updateimg do
  require 'fileutils'
  `dd if=/dev/zero of=/tmp/updates.img bs=1k count=2440`
  `mkfs.ext2 -F /tmp/updates.img`
  `sudo mount -o loop /tmp/updates.img /mnt/`
  Dir['anaconda-11.1.2.195/*.py'].each do |f|
    FileUtils.cp f, '/mnt/'
  end
  Dir['anaconda-11.1.2.195/installclasses/*.py'].each do |f|
    FileUtils.cp f, '/mnt/'
  end
  Dir['anaconda-11.1.2.195/ui/*'].each do |f|
    FileUtils.cp f, '/mnt/'
  end
  Dir['anaconda-11.1.2.195/iw/*'].each do |f|
    FileUtils.cp f, '/mnt/'
  end
  `sudo umount /mnt/`
  `scp /tmp/updates.img ruido:/var/www/mirror/`
end
