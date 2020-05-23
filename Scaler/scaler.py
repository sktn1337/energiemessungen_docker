#Author Sandro Kreten
import scipy.integrate
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy import interpolate
from scipy import optimize

############# Messung vor der Skalierung #####################################

## Messunge nach Simulation
x = np.array([6688,16360,20136,25496,34500,36784,43368,48648,49900,50876]) #Zugriffe
y = np.array([0.719,0.754,0.789,0.823,0.878,0.899,0.928,0.952,0.964,0.970]) #Watt normalisiert
conc = np.array([0.042,0.121,0.194,0.249,0.376,0.394,0.641,0.803,0.922,1.000]) #Concurrency-Faktor normalisiert
cpu = np.array([24.8,49.24,59.2,70.12,78.16,80.88,88.2,94,97.48,99.2])

print("Werte gesetzt")
############# Kubische Splines der Messungen ################################
yint = interpolate.UnivariateSpline(x,y , k=3)(x) 
yint2 = interpolate.UnivariateSpline(x,conc, k=3)(x) 
y_cpu = interpolate.UnivariateSpline(x,cpu, k=3)(x) 


#Bestimme Funktionen vor der Skalierung
fwatt = np.polyfit(x,yint,6)
fconc = np.polyfit(x,yint2,6)
fcpu  = np.polyfit(x,y_cpu,6)
pwatt = np.poly1d(fwatt)
pconc = np.poly1d(fconc)
pcpu = np.poly1d(fcpu)
print("Funktionen approximiert")

################ Messungen nach Skalierung #####################################

##Simulation
xskal = np.array([7904,15368,22192,27696,34200,38760,42340,44400,51452,52584]) #Zugriffe
yskal = np.array([0.729,0.764,0.827,0.850,0.899,0.925,0.948,0.968,0.985,1.000]) #Watt normalisiert
kskal = np.array([0.024,0.058,0.089,0.118,0.164,0.222,0.275,0.319,0.448,0.550])  #Concurrency-Faktor normalisiert

####################Kubische Splines der Messungen############################
yinterp = interpolate.UnivariateSpline(xskal,yskal , k=3)(x) 
yinterp2 = interpolate.UnivariateSpline(xskal,kskal, k=3)(x) 


#################Bestimme Funktionen
fwattskal = np.polyfit(xskal,yinterp,6)
fconcskal = np.polyfit(xskal,yinterp2,6)
pwattskal = np.poly1d(fwattskal)
pconcskal = np.poly1d(fconcskal)

##################Bestimme die Deltafunktionen und dessen Maximum
deltaWatts = pwattskal - pwatt
deltaconc = pconc - pconcskal

####################Bestimme obere und unter Schranke
maximum=0
minimum=sys.maxsize

if(x[len(x)-1]>xskal[len(xskal)-1]):
    maximum=xskal[len(xskal)-1]
else:
    maximum=x[len(x)-1] 

if(x[0]<xskal[0]):
    minimum=xskal[0]
else:
    minimum=x[0] 

##Bestimme Minimum des Leistungsaufnahmedeltas

min=minimum
t=minimum
   
while(t<maximum):
    if(deltaWatts(t)<deltaWatts(min)):
        min=t
    t=t+1

##Bestimme halbiertes Maximum des Nebenläufigkeitsdeltas
c2=minimum
newDelta=-0.5
while(newDelta<(deltaconc(maximum)/2)):
    c2=c2+0.5
    newDelta=deltaconc(c2)
   

ScalingPoint=(c2+min)/2
print(ScalingPoint) 
print("Scaling point CPU-Percent:"+str(pcpu(ScalingPoint)))
print("Scaling point (MAX) CPU-Percent:"+str(pcpu(c2)))
print("Scaling point (MIN) CPU-Percent:"+str(pcpu(min)))

####Zeige die Ergebnisse in Form von matplot-Charts
#plt.title("Ermitteltes Skalierungsintervall")
#plt.xlabel('CPU-Auslastung in %')
#plt.plot(x,pwatt(x),'g' ,label = 'interpolierte Leistungsaufnahme')
#plt.plot(cpu,y, 'g', label = 'Original Leistungsaufnahme')
#plt.plot(x,pconc(x) ,label = 'interpolierte Erreichbarkeit')
#plt.plot(x, y, 'go', label = 'Original Leistungsaufnahme skaliert')
#plt.plot(cpu, conc, 'b', label = 'Original Erreichbarkeit')
#plt.plot(xskal, pwattskal(xskal),'b' ,label = 'interpolierte Leistungsaufnahme skaliert')
#plt.plot(xskal, pconcskal(xskal), 'b', label = 'interpolierte Erreichbarkeit skaliert')
#plt.plot(x, deltaWatts(x), color='b', label = 'Leistungsaufnahmedelta')
#plt.plot(xskal, deltaconc(xskal),color="g", label = 'Erreichbarkeitdelta')
#plt.axvline(min,color='b',linestyle='--')
#plt.plot(min,deltaWatts(min),'bo',label="Leistungsaufnahme Minumum")
#plt.axvline(c2,color='g',linestyle='--')
#plt.plot(c2,deltaconc(c2),'go',label="Erreichbarkeit Maximum/2")
#plt.axvline(ScalingPoint,color='r')
#plt.plot(pcpu(ScalingPoint),0,'ro',label="Skalierungspunkt")
#plt.axvline(pcpu(ScalingPoint),color='r')
#plt.plot(pcpu(min),0,'bo',label="Untere Schranke des Skalierungsintervalls")
#plt.axvline(pcpu(min),color='b',linestyle='--')
#plt.plot(pcpu(c2),0,'yo',label="Obere Schranke des Skalierungsintervalls")
#plt.axvline(pcpu(c2),color='y',linestyle='--')
#plt.plot(maximum,deltaconc(maximum),'yo',label="Concurrency Maximum")
#plt.plot(c2,deltaconc(c2),'go',label="Concurrency Maximum durch 2")
#plt.legend(loc="bottom right",ncol=1,prop={'size':8})
#plt.savefig("C:\\Users\\krete\\scaler\\Skalierungsintervall.png", bbox_inches="tight")
#plt.show()