import sys
import sqlite3
import libvirt
import json
import csv
pm_file=sys.argv[1]
print "Physical machine file ",pm_file
try:
	print "Database configuration going"
	db=sqlite3.connect('mycloud.db')
	cur=db.cursor()
	cur.execute("drop table if exists vm_entry");
	cur.execute("drop table if exists x_entry");
	cur.execute("drop table if exists pm_entry");
	cur.execute("create table vm_entry(vname text,pmid int,ip text,vmid int,cores int,instance_type int)");
	cur.execute("create table x_entry(x int)");
	cur.execute("create table pm_entry(pmid int,ip text)");
	cur.execute("insert into x_entry values(100)")
	with open(pm_file) as data_file:    
		data = json.load(data_file)
	n=len(data["pms"])
	#Number of physical machines
	#~ print n 
	for i in range(n):
		cur.execute("insert into pm_entry values("+str(i+1)+","+"'"+str(data["pms"][i])+"'"+")")
	db.commit();
	db.close()
	print "Database successfully configured "
except Exception as e:
	print str(e)
