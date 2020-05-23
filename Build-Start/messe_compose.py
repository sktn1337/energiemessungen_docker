#! /usr/bin/env python
from datetime import datetime
from subprocess import Popen, PIPE
import time
import sys
import os
import threading
import commands
import json

#############################################default IPs######################################################################
PDU_IP='192.168.178.72'
DOCKER_HOST_API='192.168.0.2:2375'
############################################################################
Volt=0
Ampere=0
PowerFactor=0
sum=0
count=0
overall_counter=0
avg_watts=[]


def getSNMP(IP, OID, unit):
	process = Popen("snmpget -v1 -c private "+str(IP)+" "+str(OID),stdout=PIPE, shell=True)
	while True:
		line=process.stdout.readline().rstrip()

		if not line:

			break
		line=line.split(":")
		
		return line[1]


def data_collector(event):
    global count
    global sum
    global overall_counter
    global Ampere
    global Volt
    global PowerFactor
    global xs
    global ys
    start_time = time.time()
    while True:
        # Strom
        Ampere = getSNMP("192.168.178.72", "1.3.6.1.4.1.28507.43.1.5.1.2.1.5.1", "mA")
        # Volt
        Volt = getSNMP("192.168.178.72", "1.3.6.1.4.1.28507.43.1.5.1.2.1.6.1", "V")
        # PowerFactor
        PowerFactor = getSNMP("192.168.178.72", "1.3.6.1.4.1.28507.43.1.5.1.2.1.8.1", "PF")
        # Watt
        activeWatt = float(int(Volt) * int(Ampere) * int(PowerFactor)) / (1000 * 1000)
        sum = sum + activeWatt
        count += 1
        if event.is_set():
                for x in avg_watts:
		     sum=sum+x
                print "Gesamtverbrauch:"+str(round(sum/count,3))+"\n"	   
		break


for x in range(1,11):
   event=threading.Event()
   data_thread=threading.Thread(target=data_collector,args=(event,))
   print("Nummer "+str(x)+"   #############################Build Prozess des Image wird gestartet##############################")
      


   time.sleep(10)
   #############Starte Messung und Zeit
   data_thread.start()
   start_time = time.time()


   #########################rm
   #command ="sshpass -p '123456' ssh udoo@udoo 'cd /home/udoo/go_api; docker-compose -f docker-compose.yaml up -d'"
   command ="sshpass -p '123456' ssh udoo@udoo 'cd /home/udoo/go_api; docker-compose -f docker-compose.api.yaml up -d'"
   status, out=commands.getstatusoutput(command)
   print(status)
   print(out)
   
   #############event feuern und Zeit stoppen
   event.set()
   print("Dauer: "+str(round(time.time()-start_time,3))+" Sekunden")
  

   ###############
   time.sleep(10)
   #command ="sshpass -p '123456' ssh udoo@udoo 'cd /home/udoo/go_api; docker-compose -f docker-compose.yaml down'"
   command ="sshpass -p '123456' ssh udoo@udoo 'cd /home/udoo/go_api; docker-compose down --remove-orphans'"
   status, out=commands.getstatusoutput(command)
   print(status)
   print(out)

   time.sleep(10)

	

