from flask import Flask, request, url_for
from flask import jsonify
import libvirt
import sys
import json
import csv
import re
from pprint import pprint
from random import randint
import sqlite3
import os
app = Flask(__name__)

def get_anyfourdigit():
	return randint(1000, 10000)
dump_xml = "<domain type='kvm' id='4'>, '\
  <name>Win8</name>, '\
  <uuid>75d9dd16-6232-4edf-0281-e871ad7cbbf7</uuid>, '\
  <cpu>,'\
  <topology cores='4' sockets='1' threads='1' />,'\
   </cpu>,'\
  <memory unit='MB'>2048</memory>,'\
  <currentMemory unit='MB'>2048</currentMemory>,'\
  <vcpu placement='static'>1</vcpu>, '\
  <resource>, '\
    <partition>/machine</partition>, '\
  </resource>, '\
  <os>, '\
    <type arch='x86_64' machine='pc-i440fx-trusty'>hvm</type>, '\
    <boot dev='hd'/>, '\
  </os>, '\
  <features>, '\
    <acpi/>, '\
    <apic/>, '\
    <pae/>, '\
  </features>, '\
  <clock offset='utc'/>, '\
  <on_poweroff>destroy</on_poweroff>, '\
  <on_reboot>restart</on_reboot>, '\
  <on_crash>restart</on_crash>, '\
  <devices>, '\
    <emulator>/usr/bin/kvm-spice</emulator>, '\
    <disk type='file' device='disk'>, '\
      <driver name='qemu' type='raw'/>, '\
      <source file='/var/lib/libvirt/images/Win7.img'/>, '\
      <target dev='hda' bus='ide'/>, '\
      <alias name='ide0-0-0'/>, '\
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>, '\
    </disk>, '\
    <disk type='block' device='cdrom'>, '\
      <driver name='qemu' type='raw'/>, '\
      <target dev='hdc' bus='ide'/>, '\
      <readonly/>, '\
      <alias name='ide0-1-0'/>, '\
      <address type='drive' controller='0' bus='1' target='0' unit='0'/>, '\
    </disk>, '\
    <controller type='usb' index='0'>, '\
      <alias name='usb0'/>, '\
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>, '\
    </controller>, '\
    <controller type='pci' index='0' model='pci-root'>, '\
      <alias name='pci.0'/>, '\
    </controller>, '\
    <controller type='ide' index='0'>, '\
      <alias name='ide0'/>, '\
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>, '\
    </controller>, '\
    <interface type='network'>, '\
      <mac address='52:54:00:09:fa:89'/>, '\
      <source network='default'/>, '\
      <target dev='vnet0'/>, '\
      <model type='rtl8139'/>, '\
      <alias name='net0'/>, '\
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>, '\
    </interface>, '\
    <serial type='pty'>, '\
      <source path='/dev/pts/15'/>, '\
      <target port='0'/>, '\
      <alias name='serial0'/>, '\
    </serial>, '\
    <console type='pty' tty='/dev/pts/15'>, '\
      <source path='/dev/pts/15'/>, '\
      <target type='serial' port='0'/>, '\
      <alias name='serial0'/>, '\
    </console>, '\
    <input type='mouse' bus='ps2'/>, '\
    <input type='keyboard' bus='ps2'/>, '\
    <graphics type='vnc' port='5900' autoport='yes' listen='127.0.0.1'>, '\
      <listen type='address' address='127.0.0.1'/>, '\
    </graphics>, '\
    <sound model='ich6'>, '\
      <alias name='sound0'/>, '\
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>, '\
    </sound>, '\
    <video>, '\
      <model type='cirrus' vram='9216' heads='1'/>, '\
      <alias name='video0'/>, '\
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>, '\
    </video>,'\
    <memballoon model='virtio'>,'\
      <alias name='balloon0'/>, '\
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>, '\
    </memballoon>, '\
  </devices>, '\
  <seclabel type='dynamic' model='apparmor' relabel='yes'>, '\
    <label>libvirt-75d9dd16-6232-4edf-0251-e871ad7cbbf7</label>, '\
    <imagelabel>libvirt-75d9dd16-6232-4edf-0251-e871ad7cbbf7</imagelabel>, '\
  </seclabel>, '\
</domain>"

@app.route('/')
def front_page():
	return "Cloud Virtualization Orchestration Layer";

#http://server/vm/create?name=test_vm&instance_type=type -- VM creation
@app.route('/vm/create')
def mycreate():
	try:
		global dump_xml
		temp=dump_xml;
		vm_type=sys.argv[1]
		image_types=sys.argv[2]
		print image_types
		db=sqlite3.connect('mycloud.db')
		cur=db.cursor()
		record=cur.execute("select * from x_entry")
		record=cur.fetchone()
		x=int(record[0]);
		y=x;
		name=request.args.get('name');
		instance_type=request.args.get('instance_type');
		iit=int(request.args.get('image_id'))
		#~ print "i m here"
		with open(image_types) as data_file:    
			data = json.load(data_file)
		print data["images"]
		n=len(data["images"])
		print str(n)
		if(iit>n):
			return "Invalid Image Id"
		else:
			imaddr=data["images"][iit-1]
		print imaddr
		record=cur.execute("select * from pm_entry ")
		check_flag=0;
		for j in record:
			pmid=j[0]
			ip=j[1]
			print str(ip)
			conn=libvirt.open("qemu+ssh://"+ip+"/system")
			tt=conn.getCapabilities();
			l=re.search("<memory unit='KiB'>",tt).start()+19;
			r=re.search("</memory>",tt).start();
			l2=re.search('cpus num=',tt).start();
			s=""
			for i in range(l,r):
				s+=tt[i]
			total_mem=int(s);
			s=""
			s=conn.getFreeMemory()
			free_mem=int(s)/1024; #which is in bytes
			s=""
			flag=0;
			for i in range(l2,l2+100):
				if(flag==1 and tt[i]=='>'):
					break;
				if flag==1:
					if(tt[i]>='0' and tt[i]<='9'):
						s+=tt[i];
				else:
					if(tt[i]=='='):
						flag=1;
						i+=1
			my_cpu=int(s);
			lll=imaddr.split('/')
			lll=lll[len(lll)-1]
			print lll
			#~ os.system("scp "+imaddr+" "+ str(ip)+":~/")
			print str("scp "+imaddr+" "+ str(ip)+":~/")
			dump_xml=dump_xml.replace("<name>Win8</name>","<name>"+name+"</name>");
			dump_xml=dump_xml.replace("<uuid>75d9dd16-6232-4edf-0281-e871ad7cbbf7</uuid>","<uuid>75d9dd16-"+str(get_anyfourdigit())+"-4edf-0281-e871ad7cbbf7</uuid>");
			uname=ip.split('@')
			uname=uname[0]
			dump_xml=dump_xml.replace("/var/lib/libvirt/images/Win7.img","/home/"+uname+"/"+str(lll));
			print dump_xml
			
			with open(vm_type) as data_file:    
				data = json.load(data_file)
			nr=int(data["types"][int(instance_type)-1]["ram"]) #RAM need
			if nr>=free_mem:
				dump_xml=temp;
				continue;
			print "here"
			nc=int(data["types"][int(instance_type)-1]["cpu"]) #cpu need
			record=db.execute("Select * from vm_entry where pmid ="+str(pmid));
			current=0;
			for i in record:
				print i
				current+=int(i[4]);
			print "here "+str(current)+" "+str(nc)+" "+str(my_cpu)
			if nc>(my_cpu-current):
				dump_xml=temp;
				continue;
			else:
				print "Memory is allocatable"
				check_flag=1;
				dump_xml=dump_xml.replace("unit='MB'>2048","unit='MB'>"+str(nr));
				dump_xml=dump_xml.replace("cores='4'","cores='"+str(data["types"][int(instance_type)-1]["cpu"])+"'");
				conn.defineXML(dump_xml);
				dump_xml=temp
				x+=1;
				dom = conn.lookupByName(name)
				dom.create()
				#~ dom = conn.lookupByN(vmid)
				infos = dom.info()
				print 'ID = %d' % x
				print 'Name =  %s' % dom.name()
				print 'State = %d' % infos[0]
				print 'Max Memory = %d' % infos[1]
				print 'Number of virt CPUs = %d' % infos[3]
				print 'CPU Time (in ns) = %d' % infos[2]
				#~ conn.close();
				break;
		#~ print "Hello "+instance_type
		if check_flag==1:
			print "Updated"
			cur.execute("update x_entry set x="+str(x)+" where x = "+str(y))
			cur.execute("insert into vm_entry (vname,pmid,ip,vmid,cores,instance_type) values ("+"'"+str(name)+"'"+","+str(pmid)+","+"'"+str(ip)+"'"+','+str(x)+","+str(nc)+","+str(instance_type)+")");
			db.commit();
			db.close();
			conn.close();
			#~ return jsonify(Id=x,Name=name,State=infos[0],Ram=infos[1],Number_of_virt_CPUs=infos[3],CPU_Time_Nano_Seconds=infos[2],Pmid=pmid);
			return jsonify(vmid=x);
		else:
			print "---flag value is "+str(flag)
			try:
				db.close();
				conn.close();
			except Exception as e:
				print str(e)
				pass
			return "0\n"
			#~ return "Sorry, problem creating VM.\nNot enough resources available"
	except Exception as e:
		print str(e)
		dump_xml=temp
		try:
			conn.close();
		except:
			pass
		print str(e) 
		return "0\n"
		#~ return "Sorry, problem creating VM"

#http://server/vm/query?vmid=vmid  --VM Query
@app.route('/vm/query')
def vm_query():
	try:
		vmid=int(request.args.get('vmid'));
		db=sqlite3.connect('mycloud.db')
		cur=db.cursor()
		record=cur.execute("Select * from vm_entry where vmid = "+str(vmid));
		i=0;
		for j in record:
			print j
			i+=1
			name= j[0]
			print j[1]
			ip=str(j[2])
			it=int(j[5]) #Instance type
			pmid=int(j[1])
			print "ip is "+ip
			break;
		db.close();
		if(i==0):
			return "0\n"
			#~ return "Sorry no such such Vm exists"
		print ip
		conn=libvirt.open("qemu+ssh://"+ip+"/system")
		dom = conn.lookupByName(name)
		#~ dom = conn.lookupByN(vmid)
		infos = dom.info()
		print 'ID = %d' % vmid
		print 'Name =  %s' % dom.name()
		print 'State = %d' % infos[0]
		print 'Max Memory = %d' % infos[1]
		print 'Number of virt CPUs = %d' % infos[3]
		print 'CPU Time (in ns) = %d' % infos[2]
		conn.close();
		#~ return jsonify(Id=vmid,Name=dom.name(),State=infos[0],RAM=infos[1],Number_of_virt_CPUs=infos[3],CPU_Time_Nano_Seconds=infos[2]);
		return jsonify(vmid=vmid,name=dom.name(),instance_type=it,pmid=pmid);
	except Exception as e:
		print str(e)
		return "Sorry no such VmId exists"
@app.route('/vm/destroy')
def destroy():
	try:
		vmid=int(request.args.get('vmid'));
		db=sqlite3.connect('mycloud.db')
		cur=db.cursor()
		record=cur.execute("Select * from vm_entry where vmid = "+str(vmid));
		i=0;
		for j in record:
			i+=1
			name= j[0]
			print j[1]
			ip=str(j[2])
			print "ip is "+ip
			break;
		if(i==0):
			return "0"
			#~ return "Sorry no such such Vm exists"
		print ip
		conn=libvirt.open("qemu+ssh://"+ip+"/system")
		dom = conn.lookupByName(name)
		try:
			dom.destroy(); #shutdown
		except:
			pass
		dom.undefine(); #Make Vm Dead
		cur.execute("delete from vm_entry where vmid= "+str(vmid));
		db.commit();
		db.close();
		conn.close();
		return "1";
		#~ return "VM successfully destroyed";
	except:
		return "0"
		#~ return "Sorry no such VmId exists"
@app.route('/vm/types')
def vm_types():
	vm_type=sys.argv[1]
	r = ""
	with open(vm_type) as f:
		r=json.load(f)
	return jsonify(r)

@app.route('/pm/list')
def pm_list():
	db=sqlite3.connect('mycloud.db')
	cur=db.cursor()
	record=cur.execute("Select * from pm_entry");
	y=[]
	for j in record:
		print j[0]
		y.append(j[0]);
	db.close()
		#~ return dom.name()+" with Id "+str(x)+" Created successfully :)"
	return jsonify(pmids=y);
	
@app.route('/image/list')
def image_list():
	image_types=sys.argv[2]
	with open(image_types) as data_file:    
			data = json.load(data_file)
	x=[]
	n=len(data["images"])
	for i in range(n):
		ml=data["images"][i].split('/') #list
		n=len(ml)
		ml=ml[n-1].split('.')
		y=ml[0]
 		x.append({'id':i+1,'name':y});
		#~ return dom.name()+" with Id "+str(x)+" Created successfully :)"
	return jsonify(images=x);
	
@app.route('/pm/query')
def pm_query():
	try:
		mc=0
		db=sqlite3.connect('mycloud.db')
		cur=db.cursor()	
		pmid=int(request.args.get('pmid'));
		global dump_xml
		temp=dump_xml;
		name=request.args.get('name');
		instance_type=request.args.get('instance_type');
		record=cur.execute("select * from pm_entry where pmid = "+str(pmid))
		for j in record:
			print j
			pmid=j[0]
			ip=j[1]
			conn=libvirt.open("qemu+ssh://"+ip+"/system")
			tt=conn.getCapabilities();
			l=re.search("<memory unit='KiB'>",tt).start()+19;
			r=re.search("</memory>",tt).start();
			l2=re.search('cpus num=',tt).start();
			s=""
			for i in range(l,r):
				s+=tt[i]
			total_mem=int(s);
			s=""
			s=conn.getFreeMemory()
			free_mem=int(s)/1024; #which is in bytes
			s=""
			flag=0;
			for i in range(l2,l2+100):
				if(flag==1 and tt[i]=='>'):
					break;
				if flag==1:
					if(tt[i]>='0' and tt[i]<='9'):
						s+=tt[i];
				else:
					if(tt[i]=='='):
						flag=1;
						i+=1
			my_cpu=int(s);
			record=db.execute("Select * from vm_entry where pmid ="+str(pmid));
			current=0;
			for i in record:
				mc+=1
				print i
				current+=int(i[4]);
		x=[]
		x.append({'Pmid':pmid,'Capacity':{'Cpu':my_cpu,'Ram':total_mem/1024},'Free':{'Cpu':my_cpu-current,'Ram':free_mem/1024},'Vms':mc});
		conn.close();
		db.close()
		#~ return dom.name()+" with Id "+str(x)+" Created successfully :)"
		return jsonify(lists=x);
	except Exception as e:
		print str(e)
		return "Invalid Physical Machine Id"


@app.route('/pm/listvms')
def pm_vmlist():
	db=sqlite3.connect('mycloud.db')
	cur=db.cursor()
	pmid=int(request.args.get('pmid'));
	record=cur.execute("Select * from pm_entry where pmid = "+str(pmid));
	i=0;
	for j in record:
		i+=1
		ip= j[1]
		break;
	if i==0:
		db.close()
		return "0\n"
		#~ return "Sorry Invalid Physical Machine"
	else:
		conn=libvirt.open("qemu+ssh://"+ip+"/system")
		tt=conn.getCapabilities();
		l=re.search("<memory unit='KiB'>",tt).start()+19;
		r=re.search("</memory>",tt).start();
		s=""
		for i in range(l,r):
			s+=tt[i]
		#~ print s
		total_mem=int(s);
		s=""
		s=conn.getFreeMemory()
		free_mem=int(s)/1024;
		x=[]
		for name in conn.listDefinedDomains():
			try:
				dom = conn.lookupByName(name)
				query="Select * from vm_entry where pmid = "+str(pmid) + " and vname = "+"'"+str(dom.name())+"'" ;
				print query
				cur.execute("Select * from vm_entry where pmid = "+str(pmid) + " and vname = "+"'"+str(dom.name())+"'" );
				#~ print "here"
				record=cur.fetchall()
				if(len(record)==0):
					continue
				i=0;
				for j in record:
					print j
					i+=1
					vmid= j[3]
					break;
				if(i==0):
					break;
				infos = dom.info()
				print "shutoff"
				print 'ID = %d' % vmid
				print 'Name =  %s' % dom.name()
				print 'State = %d' % infos[0]
				print 'Max Memory = %d' % infos[1]
				print 'Number of virt CPUs = %d' % infos[3]
				print 'CPU Time (in ns) = %d' % infos[2]
				x.append(vmid);
			except Exception as e:
				print str(e)
				continue
		for id in conn.listDomainsID():
			try:
				dom = conn.lookupByID(id)
				query="Select * from vm_entry where pmid = "+str(pmid) + " and vname = "+"'"+str(dom.name())+"'" ;
				print query
				cur.execute("Select * from vm_entry where pmid = "+str(pmid) + " and vname = "+"'"+str(dom.name())+"'" );
				#~ print "here"
				record=cur.fetchall()
				if(len(record)==0):
					continue
				i=0;
				for j in record:
					print j
					i+=1
					vmid= j[3]
					break;
				if(i==0):
					break;
				infos = dom.info()
				print "running"
				print 'ID = %d' % vmid
				print 'Name =  %s' % dom.name()
				print 'State = %d' % infos[0]
				print 'Max Memory = %d' % infos[1]
				print 'Number of virt CPUs = %d' % infos[3]
				print 'CPU Time (in ns) = %d' % infos[2]
				x.append(vmid);
			except Exception as e:
				print str(e)
				continue
			#~ x.append({'Id':vmid,'Name':dom.name(),'State':infos[0],'MaxMemory_KBs':infos[1],'Number_of_virt_CPUs':infos[3],'CPU_Time_Nano_Seconds':infos[2]});
		conn.close();
		db.close()
		#~ return dom.name()+" with Id "+str(x)+" Created successfully :)"
		return jsonify(vmids=x);

if __name__ == '__main__':
	app.run(port=5002,debug=True)
	
