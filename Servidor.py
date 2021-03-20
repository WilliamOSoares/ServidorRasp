#!/usr/bin/env python3
from __future__ import print_function
import time
from datetime import datetime
import mercury

# An extremely simple HTTP server
import socket, sys, time
# Server runs on all IP addresses by default
HOST=''
#HOST = 'localhost'
# 8080 can be used without root priviledges
PORT=5021
#BUFLEN=8192 # buffer size

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	print ("Server iniciado na porta -> ", PORT, socket.gethostname())
	s.bind((HOST,PORT))
except socket.error :
	print ("Nao foi possivel conectar a porta: ",PORT)
	print (socket.error)
	sys.exit(-1)

s.listen(1)

reader = mercury.Reader("tmr:///dev/ttyUSB0", baudrate=230400)
reader.set_region("NA2")
reader.set_read_plan([1], "GEN2", read_power=1500)
#print(reader.read())

tags = list(map(lambda t: t.epc, reader.read()))
array = []

for x in range(len(tags)):
    dado = str(tags[x])
    print(dado)
    array.append(dado+"\n")

while True:
	con, cliente = s.accept()
	print ('Concetado por', cliente)
	while True:
		msg = con.recv(1024)
		if not msg: break
		#print (msg.decode("utf-8"))
		print (msg)
		for y in range(len(tags)):
			msg2 = str.encode(array[y])
			type(msg2)
			print(array[y])
			con.send(msg2)
			#for z in range(5):
				#print(z)
	print ('Finalizando conexao do cliente', cliente)
	con.close()
