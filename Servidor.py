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
		print ('Iniciando...')
		recb = con.recv(1024).decode()
		if not recb: break
		arq.write(recb + "\n")
		print ('Arquivo enviado!')
	arq.close()
	print ('Finalizando conexao do cliente', cliente)
	con.close()


'''
import socket, threading

class RIFDThread(threading.Thread):	
	
	def __init__():
		arq = open('configInicial.txt','r')
		textPortaSerial = arq.readline()
		textBaudrate = arq.readline()
		textRegiao = arq.readline()
		textAntena = arq.readline()
		textProtocolo = arq.readline()
		textPower = arq.readline()

	def run():

'''