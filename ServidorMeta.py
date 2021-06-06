from __future__ import print_function
from datetime import datetime, timedelta
from LeituraCarros import *
from threading import *
import mercury, time, socket, sys, time, os, json, timeit


leituras = []
cont = 0

leituras.append(leituraCarro("0", "rssi", "2021-04-27 20:00:54.616000"))
leituras.append(leituraCarro("1", "rssi", "2021-04-27 20:05:54.616000"))
leituras.append(leituraCarro("2", "rssi", "2021-04-27 20:10:54.616000"))
a = "2021-04-27 20:01:57.606000"
b = "2021-04-27 20:06:50.610000"
c = "2021-04-27 20:11:57.016000"

for x in range(len(leituras)):
	for i in range(len(leituras)):
		if (leituras[i].epc == str(cont)):
			if(cont == 0):
				print("entrou")
				print(leituras[i].validaTempo(a,"1"))
			elif(cont == 1):
				print("entrou")
				print(leituras[i].validaTempo(b,"1"))
			elif(cont == 2):
				print("entrou")
				print(leituras[i].validaTempo(c,"1"))
	cont = cont+1

for j in range(len(leituras)):
	print(leituras[j].epc+" - "+ leituras[j].tempo)