#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
import mercury, time, socket, sys, time, os

HOST=''
PORT=5021

def crud(con):
	arq = open('requisito.txt','r')
	req = arq.readline().strip("\n")
	if(req == "configLeitor"):
		configLeitor(arq,con)
	elif(req == "att"):
		atualizacao(arq,con)

def configLeitor(arq):
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
	for x in array:
		con.sendall([type]array[x])
	#Tem que testar

def atende(con):
	arq = open('requisito.txt','w+')
	while True:
		print ('Iniciando...')
		recb = con.recv(1024).decode()
		if not recb: break
		arq.write(recb + "\n")
		print ('Arquivo enviado!')
	arq.close()
		
def atualizacao(arq,con)
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

while 1:
	con, cliente = s.accept()
	print ('Concetado por', cliente)
	atende(con)
	crud(con)
	print ('Finalizando conexao do cliente', cliente)
	con.close()
