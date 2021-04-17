#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
from LeituraCarros import leituraCarro
from threading import *
import mercury, time, socket, sys, time, os, json, timeit

HOST=''
PORT=5021
portaSerial = ""
baud = 0
regiao = ""
antena = 0
protocolo = ""
readPower = 0
voltas = 0
tempoMin = 0
tempoQuali = 0
dadosDaLeitura = []
cicloLeitura = 0
length_max = 0
trava = BoundedSemaphore(1)
online = True
reader = mercury.Reader("tmr:///dev/ttyUSB0", baudrate=230400)

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

def dadosCorrida(con, arqJson):
	global voltas, tempoMin, tempoQuali, length_max
	voltas = int(arqJson['Voltas'])
	tempoQuali = int(arqJson['Quali'])*60
	tempoMin = int(arqJson['TempoMin'])*60
	mensagem = '{"URL":"dadosCorrida", "return":"OK"}'
	length_max = int(arqJson['CarrosQuant'])
	preparacaoEnvio = mensagem + "\n"
	con.sendall(bytes(preparacaoEnvio.encode('utf-8')))

def dadosLeitura(epc, rssi, date):
	global dadosDaLeitura, length_max
	if(len(dadosDaLeitura)==0):
		leitura = leituraCarro(epc, rssi, date)
		dadosDaLeitura.append(leitura)
	elif(len(dadosDaLeitura)<length_max):
		for x in range(len(dadosDaLeitura)):
			if(dadosDaLeitura[x].epc != epc):
				leitura = leituraCarro(epc, rssi, date)
				dadosDaLeitura.append(leitura)
		
	

def refinaEnviaDado(cicloLeitura):
	global dadosDaLeitura
	if(len(dadosDaLeitura)>0):		
		preparajson = '{'
		for z in range(len(dadosDaLeitura)):
		    dadoEpc = str(dadosDaLeitura[z].epc)
		    dadoRssi = str(dadosDaLeitura[z].rssi)
		    dadoTempo = str(dadosDaLeitura[z].tempo)
		    preparajson = preparajson + '"CARRO'+str(z)+ '":"' + dadoEpc + '", "RSSI'+str(z)+ '":"' + dadoRssi + '", "TEMPO'+str(z)+ '":"' + dadoTempo + '", '
		    #print(preparajson)
		preparajson = preparajson + '"CicloLeitura":"' + str(cicloLeitura) + '", '
		size = len(preparajson)
		remove = preparajson[:size - 2]
		#print(remove)
		preparajson = remove
		preparajson = preparajson +'}'
		preparajson = preparajson +	"\n"
		print(preparajson)
		dadosDaLeitura = []
		con.sendall(bytes(preparajson.encode('utf-8')))
		return True
	else:
		return False

def produtor():
	global dadosDaLeitura, tempoQuali, cicloLeitura, trava, online, reader
	reader = iniciaLeitor()
	while online:
		print("produzindo")
		trava.acquire()	
		print("produzindo travado")
		if(online):
			reader.start_reading(lambda tag: dadosLeitura(tag.epc, tag.rssi, datetime.fromtimestamp(tag.timestamp)))
			time.sleep(1)
			reader.stop_reading()
		trava.release()

def consumidor():
	global dadosDaLeitura, tempoQuali, cicloLeitura, trava, online
	while online:
		print("consumindo")
		trava.acquire()	
		print("consumindo travado")
		if(online):
			if(refinaEnviaDado(cicloLeitura)):
				cicloLeitura+=1
		trava.release()				

def qualificatorio(con, produtor, consumidor):
	global dadosDaLeitura, tempoQuali, cicloLeitura, trava, online
	reader = iniciaLeitor()
	cicloLeitura = 0
	
	produtor.start()
	consumidor.start()
	ini = time.time()
	while (tempoQuali>0):
		time.sleep(5)
		fim = time.time()
		if ((fim-ini)>=tempoQuali):
			tempoQuali=0
		print (fim-ini)	
	if (tempoQuali==0):
		time.sleep(5)
	trava.acquire()
	online = False
	trava.release()
	print ("acabou o qualificatorio")
	acabouQuali(con)

def acabouQuali(con):
	alerta = '{"URL":"finalQuali", "status":"acabou", "CicloLeitura":"' + str(cicloLeitura) + '"}'
	preparacaoEnvio = alerta + "\n"
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
	con.sendall(bytes(preparajson.encode('utf-8')))

def atende(con, produtor, consumidor):
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
				dadosCorrida(con, dados)
			elif(dados['URL'] == "retornaEPC"):
				retornaEPC(con)
			elif(dados['URL'] == "comecaQuali"):
				qualificatorio(con, produtor, consumidor)

		else:
			print("Não é um POST e nem um GET")
		print ('requisição finalizada!')

produtor = Thread(target=produtor)
consumidor = Thread(target=consumidor)
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
	atende(con, produtor, consumidor)	
	
print ('Finalizando conexao do cliente', cliente)
con.close()
