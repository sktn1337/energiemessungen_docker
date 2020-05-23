#! /usr/bin/env python
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Author Sandro Kreten
#Python 2.7 optimiert

from datetime import datetime
from subprocess import Popen, PIPE
import time
import sys
import os
import threading
import commands
import docker
import json

#############################################default IPs######################################################################
PDU_IP='192.168.178.72'
DOCKER_HOST_API='192.168.0.2:2375'

##############################################default values###################################################################
#Energy Variables
Volt=0
Ampere=0
PowerFactor=0
#Amount of Users
users=0
#Measurement Variables
number_of_measurements=0
sum_of_all_powers=0
#default delay
delay=0.2
#default hits
hits=100
#default duration
duration="15"
########################################variables for concurrent use###########################################################
isAlive=0
siege_events=[]
flag=0
####################################################getCPUusage################################################################
concurrency=""
hits=""
threads=[]
total_CPU=[]
total_RAM=[]
measuring_counter=[]
measuring_counter_ram=[]
numberOfContainer=0

##############################################Overview over all Measurements###################################################
all_m=[]

##Lese den CPU-Verbrauch des Containers über die Docker-API aus
def cpu_perc(d,number):
	
	if('system_cpu_usage' in d['precpu_stats']):
		cpuDelta=float(d["cpu_stats"]["cpu_usage"]["total_usage"])-float(d["precpu_stats"]["cpu_usage"]["total_usage"]) 
	
		systemDelta=float(d["cpu_stats"]["system_cpu_usage"])-float(d["precpu_stats"]["system_cpu_usage"])
		output = cpuDelta / systemDelta * 100
		global total_CPU 
		total_CPU[number]=total_CPU[number]+output
		global measuring_counter
		measuring_counter[number]=measuring_counter[number]+1
		return output
	else:
		return 0
        
##Lese den CPU-Verbrauch des Containers über die Docker-API aus
def ram_perc(d,number):
	if('usage' in d['memory_stats']):
		cpuDelta=float(d["memory_stats"]["usage"])
	
		systemDelta=float(d["memory_stats"]["limit"])
		output = cpuDelta / systemDelta
		global total_RAM 
		total_RAM[number]=total_RAM[number]+output
		global measuring_counter_ram
		measuring_counter_ram[number]=measuring_counter_ram[number]+1
		return output
	else:
		return 0
	
##Lese die Stats des Containers aus, bis das Event getriggert wird
def getStatsOfContainer(id,number,event):
	global isCPUAlive
	output=""
	count=0
	flag=0
	for times in client.stats(id,False,True):
		data = json.loads(times)
		output=output+datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f; ")+str(cpu_perc(data,number))+"; "+str(ram_perc(data,number))+"\n"
		if event.is_set():
			break

##########################################SNMP GET ENERGY DATA##################################################################
def getSNMP(OID, unit):
	global PDU_IP
	process = Popen("snmpget -v1 -c private "+str(PDU_IP)+" "+str(OID),stdout=PIPE, shell=True)
	while True:
		line=process.stdout.readline().rstrip()

		if not line:

			break
		line=line.split(":")
		return line[1]

################################################SIEGE LOAD######################################################################
def produce_Webserver_load(p, event, u):
	global delay
	global hits
	global concurrency
	global duration
	#print("Siege is started with "+str(users)+" Users and Delay of"+str(delay)+"!!!!!")
	#siege command
	command ="siege -c "+str(u)+" -d "+str(delay)+" -t"+duration+"s "+p
	#os.system(command)
	status, out=commands.getstatusoutput(command)
	out=out.split('$')
	print(out[1])
	out1=out[1].split(':')
	out1=out1[1].split(' ')
	hits=out1[0]
	print(out[2])
	out2 = out[2].split(':')
	concurrency=out2[1]
	#shows that siege is finished
	event.set()




################################################START PROGRAMM##################################################################
#get command line data
filename = "default_energy.log"
ports = []
if len(sys.argv)>3:
	filename=str(sys.argv[1])
	users=str(sys.argv[2])
        delay=str(sys.argv[3])

#read all given ports	
for i in range(4,len(sys.argv)):
	 	ports.append(str(sys.argv[i]))
               
#remote Client
api_ip=ports[0].split(':')

#print(api_ip)
DOCKER_HOST_API="http:"+api_ip[1]+":2375"

client = docker.APIClient(base_url=DOCKER_HOST_API)
#print client.containers()
#open file and user input
file = open(filename,"a")
name_of_measurement=raw_input("What do you measure? ")
file.write(name_of_measurement+"\n")
##soll mit stets gleich Last gerechnet werden oder soll die Last nach jeder Messung linear gesteigert werden?
linear_or_static = int(input("Should the load be linear [1] or static [2]? "))
file2 = open("overall.csv","a")
file2.write(name_of_measurement+datetime.now().strftime(" %Y-%m-%d %H:%M:%S.%f")+"\n")
time.sleep(0.5)

print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

###########################################start siege-process for each given port (container that uses this port)################
for x in range(2,20,2):

	if linear_or_static==1:
		u=x
	else:
		u=users

	print "User:" + str(u) + " Delay:" + str(delay) + " Duration:" + duration
	########Event to stop Resource-Collection#################################################################################
	event = threading.Event()
	i=0
	########################Array for all Container-Resources and Starting of Threads#########################################
	for container in client.containers():
                print(container["Names"])
		total_CPU.append(0)
		total_RAM.append(0)
		measuring_counter.append(0)
		measuring_counter_ram.append(0)
		threads.append(threading.Thread(target=getStatsOfContainer, args=(container["Id"], numberOfContainer, event,)))
		threads[numberOfContainer].start()
		numberOfContainer=numberOfContainer+1
	########################Start Siege Threats################################################################################
	for member in ports:
		ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f;startTestrun\n")
		file.write(ts)
		###############Events to realize if all Siege Threads terminated#################################
		siege_events.append(threading.Event())
		threading.Thread(target=produce_Webserver_load,args=(member,siege_events[i],u,)).start()
		i=i+1

	while True:
		#############################Gude#########################################
		# Ampere
		Ampere = getSNMP("1.3.6.1.4.1.28507.43.1.5.1.2.1.5.1", "mA")
		# Volts
		Volt = getSNMP("1.3.6.1.4.1.28507.43.1.5.1.2.1.6.1", "V")
		# PowerFactor
		PowerFactor = getSNMP("1.3.6.1.4.1.28507.43.1.5.1.2.1.8.1", "PF")
		# calculate the active Watts
		activeWatt = float(int(Volt) * int(Ampere) * int(PowerFactor)) / (1000 * 1000)

		#print(str(Volt) + " " + str(Ampere) + " " + str(PowerFactor) + "\n")

		####################################count all measurements
		sum_of_all_powers+=activeWatt

		number_of_measurements+=1
		#print(str(activeWatt)+" "+str(number_of_measurements)+" "+str(sum_of_all_powers))

		###################################Wait on all Ports/Containers to be no longer under Stress##########################
		for e in siege_events:
			if e.is_set():
				isAlive=isAlive+1
                                print(isAlive) 
		if isAlive>=(len(sys.argv)-4):
			event.set()
			ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f;stopTestrun\n")
			file.write(ts)
			break
		#time.sleep(0.5)

	###############################################Print Watts####################################################################

	avg=round(sum_of_all_powers/number_of_measurements,2)

	print "\nAverage Watts: "+str(round(sum_of_all_powers/number_of_measurements,2))+" Watts"
	all_m.append(avg)
	file2.write("User:"+str(u)+" Delay:"+str(delay)+" Duration:"+duration+"s; "+str(avg)+"; "+str(hits)+"; "+str(concurrency)+"; ")

	########################################Print Container Resources#############################################################	
	counter = 0
	for container in total_CPU:
		avg_cpu=round(container/measuring_counter[counter],2)
		avg_ram=round(total_RAM[counter]/measuring_counter_ram[counter],2)
		print("Container "+str(counter+1)+" CPU: "+str(avg_cpu)+" RAM: "+str(avg_ram))
		file2.write(str(avg_cpu)+"; "+str(avg_ram)+";")
		counter=counter+1

	file2.write("\n")
	#########################################warte und setze alles zurueck#######################################
	time.sleep(1)
	number_of_measurements=0
	sum_of_all_powers=0
	isAlive=0
	siege_events = []
	threads = []
	total_CPU = []
	total_RAM = []
	measuring_counter = []
	measuring_counter_ram = []
	numberOfContainer = 0
	print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        time.sleep(10)
        
        if(linear_or_static==0 and x==10):
		break

avg_sum=0
for m in all_m:
	#print(str(m))
	avg_sum=avg_sum+m
print("Average used Power in Watts: "+str(round(avg_sum/len(all_m),2)))
file.close()
file2.close()


