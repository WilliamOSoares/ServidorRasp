#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
import mercury, time, socket, sys, time, os, json

HOST=''
PORT=2020

def crud(con):
	arq = open('requisito.txt','r')
	req = arq.readline().strip("\n")
	if(req == "configLeitor"):
		configLeitor(arq,con)
	elif(req == "att"):
		atualizacao(arq,con)

def configLeitor(arq, con):
	serial = arq.readline().strip("\n")
	baud = int(arq.readline())
	regiao = arq.readline().strip("\n")
	antena = int(arq.readline())
	gen = arq.readline().strip("\n")
	power = int(arq.readline())
	arq.close()
	reader = mercury.Reader(serial, baudrate=baud)
	reader.set_region(regiao)
	reader.set_read_plan([antena], gen, read_power=power)
	#print(reader.read())
	tags = list(map(lambda t: t.epc, reader.read()))
	array = []
	for x in range(len(tags)):
	    dado = str(tags[x])
	    print(dado)
	    array.append(dado+"\n")
	for y in range(len(array)):
		con.sendall(str.encode(array[y]))
	#Tem que testar

def atende(con):
	while True:
		print ('Iniciando...')
		recb = con.recv(1024).decode('utf-8')
		if not recb: break
		print (recb)
		dados = json.loads(recb)
		if(dados['METODO'] == "POST"):
			print(dados['URL'])
		else:
			print("Xablau")
		con.sendall(bytes(recb.encode('utf-8')))
		print ('Arquivo enviado!')		
def atualizacao(con):
	print("ó tá atualizando")

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
	#crud(con)
	
	
print ('Finalizando conexao do cliente', cliente)
con.close()
