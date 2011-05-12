groups = {
        "Cloud Nodes": {
            "Abiquo KVM": "abiquo-kvm",
            "Abiquo Xen": "abiquo-xen",
            "Abiquo VirtualBox": "abiquo-virtualbox"
            },
        "Abiquo Platform": {
            "Distributed Install": ["abiquo-server", "abiquo-v2v", "abiquo-remote-services"],
            "Monolithic Install": "abiquo-monolithic",
            "Cloud in a Box": "cloud-in-a-box"
            },
        "Storage Plugins": {
            "LVM Storage": "abiquo-lvm-storage-server",
            },
        "Additional Components": {
            "Remote Repository": "abiquo-remote-repository",
            "NFS Repository": "abiquo-nfs-repository",
            "DHCP Relay": "abiquo-dhcp-relay",
            },
        "Opscode Chef": {
            "Chef Server": "chef-server", 
            "Chef Client": "chef-client",
            }
        }

group_descriptions = {
        "Cloud Nodes": "<b>Cloud Nodes</b>\nInstall Abiquo KVM or Xen (compute) nodes.",
        "Opscode Chef": "<b>Chef</b>\nInstall Chef Server/Client components",
        "Abiquo Platform": "<b>Abiquo Platform Components</b>\nInstall selected Abiquo platform components to create a monolithic, distributed or cloud-in-a-box Abiquo installation.",
        "Storage Plugins": "<b>Storage Plugins</b>\nInstall required plugins to manage external storage such as a Linux LVM storage server.",
        "Additional Components": "<b>Additional Components</b>\nAbiquo Remote Repository, NFS Repository, etc.",
}

