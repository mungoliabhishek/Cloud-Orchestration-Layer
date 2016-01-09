Builded a Virtualization Orchestration Layer, using 

KVM (kernel Virtual manager)
Python Flask Server
Libvirt Api to manage platform virtualization.

Implementated all the API's as asked in the documentatuion pdf:

1)Resource discovery is done based on used & available memeory & CPU units with the machine.
2)Resource allocation is done via First come first serve basis, that is if a physical machine is able to fulfil the request
  then, it is configured based on which first configurable m/c was found.
3)VM_API, returns vmid on successful creation
4)VM_Query API
5)VM_Destroy API
6)VM_Types API
7)Resource Service API
		LIST_VMs API
		LIST_PMs API
		PM_Query API
8)Image Service API

9)***Use of persistent storage Python sqlite database, so database saves the configured Vms of other physical machines.

The database in persistent for the first time we need to run
sh script.sh pm_type img_type vm_type
And once everything is confugured,
python cloud_project.py vm_type img_type 


