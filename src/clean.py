import sys
import sqlite3
import libvirt
import json
import csv
pm_type=sys.argv[1]
with open(pm_type) as data_file:    
	data = json.load(data_file)
n=len(data["pms"])
print "Cleaning up stuffs" #Number of physical machines
for i in range(n):
	try:
		ip=data["pms"][i]
		conn=libvirt.open("qemu+ssh://"+ip+"/system")
		#List inactive Hosts
		for name in conn.listDefinedDomains():
			dom = conn.lookupByName(name)
			try:
				dom.undefine();
			except Exception as e:
				print str(e)
		conn.close();
	except Exception as e:
		print str(e)
print "Everything's ready"
			
