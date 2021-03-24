#!/usr/bin/env python3
from __future__ import print_function
import time
from datetime import datetime
#import mercury

# An extremely simple HTTP server
import socket, sys, time, os
# Server runs on all IP addresses by default
HOST=''
#HOST = 'localhost'
# 8080 can be used without root priviledges
PORT=5021
#BUFLEN=8192 # buffer size

def crud():
	arq = open('configInicial.txt','r')
	req = arq.readline().strip("\n")
	if(req == "configLeitor"):
		configLeitor(arq)
	else:
		print("Deu ruim")

def configLeitor(arq):
	serial = arq.readline().strip("\n")
	baud = int(arq.readline())
	regiao = arq.readline().strip("\n")
	antena = int(arq.readline())
	gen = arq.readline().strip("\n")
	power = int(arq.readline())
	arq.close()
	print(serial)
	print(baud)
	print(regiao)
	print(antena)
	print(gen)
	print(power)

crud()

'''
flname = 'configInicial.txt'
arq = open(flname,'r')

serial = arq.readline().strip("\n")
baud = int(arq.readline())
regiao = arq.readline().strip("\n")
antena = int(arq.readline())
gen = arq.readline().strip("\n")
power = int(arq.readline())

arq.close()

print(serial)
print(baud)
print(regiao)
print(antena)
print(gen)
print(power)

if (req == "configInicial")
	setarLeitor()


reader = mercury.Reader(serial, baudrate=baud)
reader.set_region(regiao)
reader.set_read_plan([antena], gen, read_power=power)
print(reader.read())

arq2 = open("tagDiponivel.txt", "a")

tags = list(map(lambda t: t.epc, reader.read()))
array = []

for x in range(len(tags)):
    dado = str(tags[x])
    print(dado)
    array.append(dado+"\n")

arq2.writelines(arry)

arq2.close()
'''
sys.exit(-1)



