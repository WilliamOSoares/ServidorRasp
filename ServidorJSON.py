#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
import mercury, time, socket, sys, time, os, json

HOST=''
PORT=2020
portaSerial = ""
baud = 0
regiao = ""
antena = 0
protocolo = ""
readPower = 0

def iniciaLeitor():
	global portaSerial, baud, regiao, antena, protocolo, readPower
	reader = mercury.Reader(portaSerial, baudrate=baud)
	reader.set_region(regiao)
	reader.set_read_plan([antena], protocolo, read_power=readPower)
	return reader

def configLeitor(arqJson):
	global portaSerial, baud, regiao, antena, protocolo, readPower
	portaSerial = arqJson['portaSerial']
	baud = int(arqJson['baudrate'])
	regiao = arqJson['regiao']
	antena = int(arqJson['antena'])
	protocolo = arqJson['protocolo']
	readPower = int(arqJson['power'])

def dadosCorrida(con):
	stringzona = '{"URL":"dadosCorrida", "return":"OK"}'
	preparacaoEnvio = stringzona + "\n"
	con.sendall(bytes(preparacaoEnvio.encode('utf-8')))

def retornaEPC(con):
	reader = iniciaLeitor()
	tags = list(map(lambda t: t.epc, reader.read()))
	preparajson = '{'
	for x in range(len(tags)):
	    dado = str(tags[x])
	    print(dado)
	    preparajson = preparajson + '"EPC'+str(x)+ '":"' + dado + '", '
	    print(preparajson)
	
	size = len(preparajson)
	remove = preparajson[:size - 2]
	print(remove)
	preparajson = remove
	preparajson = preparajson +'}'
	preparajson = preparajson +	"\n"
	print(preparajson)
	#con.sendall(bytes(preparajson.encode('utf-8')))

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
		elif(dados['METODO'] == "GET"):
			if(dados['URL'] == "dadosCorrida"):
				dadosCorrida(con)
			if(dados['URL'] == "retornaEPC"):
				retornaEPC(con)
		else:
			print("Não é um POST e nem um GET")
		print ('requisição finalizada!')

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