#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
import mercury, time, socket, sys, time, os, json

HOST=''
PORT=2020


def configLeitor(arqJson):
	reader = mercury.Reader(arqJson['portaSerial'], baudrate=int(arqJson['baudrate']))
	reader.set_region(arqJson['regiao'])
	reader.set_read_plan([int(arqJson['antena'])], arqJson['protocolo'], read_power=int(arqJson['power']))
	print(reader.read())

def atende(con):
	while True:
		print ('Iniciando...')
		recb = con.recv(1024).decode('utf-8')
		if not recb: break
		print (recb)
		dados = json.loads(recb)
		if(dados['METODO'] == "POST"):
			if(dados['URL'] == "configLeitor"):
				configLeitor(dados)
		else:
			print("GET")
		con.sendall(bytes(recb.encode('utf-8')))
		print ('Arquivo enviado!')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	print ("Server iniciado na porta -> ", PORT, socket.gethostname())
	s.bind((HOST,PORT))
except socket.error :
	print ("Nao foi possivel conectar a porta: ",PORT)
	print (socket.error)
	sys.exit(-1)

s.listen(1)
con, cliente = s.accept()
print ('Concetado por', cliente)

while 1:
	atende(con)	
	
print ('Finalizando conexao do cliente', cliente)
con.close()
