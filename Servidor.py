#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
import mercury, time, socket, sys, time, os

HOST=''
PORT=5021

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	print ("Server iniciado na porta -> ", PORT, socket.gethostname())
	s.bind((HOST,PORT))
except socket.error :
	print ("Nao foi possivel conectar a porta: ",PORT)
	print (socket.error)
	sys.exit(-1)

s.listen(1)

while True:
	con, cliente = s.accept()
	print ('Concetado por', cliente)
	arq = open('configInicial.txt','a')
	while True:
		while True:
		print ('Escutando mensagem')
		recebido = con.recv(1024).decode('utf-8')
		if not recb: break
		objetoJson = json.loads(recb)
		if(objetoJson['METODO'] == "POST"):
			readPower = int(objetoJson['power'])
			protoc = objetoJson['protocolo']
			nAntena = int(objetoJson['antena'])
			regiao = objetoJson['regiao']
			baudrate = int(objetoJson['baudrate'])
			portaSerial = objetoJson['portaSerial']
			reader = mercury.Reader(portaSerial, baudrate=baudrate)
			reader.set_region(regiao)
			reader.set_read_plan([nAntena], protoc, read_power=readPower)
			print(reader.read())
		else:
			print("GET")
		con.sendall(bytes(recb.encode('utf-8')))
	arq.close()
	print ('Finalizando conexao do cliente', cliente)
	con.close()
