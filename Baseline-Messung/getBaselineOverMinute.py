#! /usr/bin/env python
##Python 2.7 optimiert

from datetime import datetime
from subprocess import Popen, PIPE
import time
import sys

Volt = 0
Ampere = 0
PowerFactor = 0

timer = 0

##Lese Daten des Gude Messgeräts aus via smtp
def getSNMP(IP, OID, unit):
    process = Popen("snmpget -v1 -c private " + str(IP) + " " + str(OID), stdout=PIPE, shell=True)
    while True:
        line = process.stdout.readline().rstrip()

        if not line:
            break
        line = line.split(":")

        return line[1]


filename = "test.log"

if len(sys.argv) > 1:
    filename = str(sys.argv[1])

file = open(str(sys.argv[1]), "w")
file.write("Day Time; active Power\n")

#Führe 10 Messungen durch
for i in range(0,10):
	sum = 0
	count = 0
	timer = 0
	avg_watts = []

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
            #Test, ob bereits eine Minute vergangen ist
    		if ((time.time() - start_time) >= 1):
        		avg = sum/count
        		#print "Mittelwert aller gemessenen Watt pro Sekunde: " + str(avg)
        		timer += 1
        		avg_watts.append(avg)
                #Schreibe Logfile
        		ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        		file.write(ts)
        		file.write("; " + str(activeWatt))
        		file.write("\n")
        		sum = 0
        		count = 0
        		start_time = time.time()
        #Bestimme Mittelwert der Messung und gebe ihn auf der Konsole aus        
   	 	if (timer >= 60):
        		for x in avg_watts:
             			sum += x
        		print "Gesamter Mittelwert: " + str(sum / len(avg_watts))
      			
    #Schlafe für 30 Sekunden und beginne Messung erneut            
	time.sleep(30)
