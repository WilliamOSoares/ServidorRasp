#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
from LeituraCarros import leituraCarro
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
	global voltas, tempoMin, tempoQuali
	voltas = int(arqJson['Voltas'])
	tempoQuali = int(arqJson['Quali'])*60
	tempoMin = int(arqJson['TempoMin'])*60
	mensagem = '{"URL":"dadosCorrida", "return":"OK"}'
	preparacaoEnvio = mensagem + "\n"
	con.sendall(bytes(preparacaoEnvio.encode('utf-8')))

def dadosLeitura(epc, rssi, date):
	global dadosDaLeitura
	print(epc,rssi,date)
	leitura = leituraCarro(epc, rssi, date)
	dadosDaLeitura.append(leitura)

def refinaEnviaDado(cicloLeitura):
	'''	
	global dadosDaLeitura
	arrayRefinado = []
	for x in range(len(dadosDaLeitura)):
		if (len(arrayRefinado)==0):
			arrayRefinado.append(dadosDaLeitura[x])
		else:
			i = 0
			for y in range(len(arrayRefinado)):
				if(dadosDaLeitura[x].epc == arrayRefinado[y].epc):
					i=1
					if (dadosDaLeitura[x].rssi > arrayRefinado[y].rssi):
						arrayRefinado[y] = dadosDaLeitura[x]
			if(i==0):
				arrayRefinado.append(dadosDaLeitura[x])
	dadosDaLeitura = []

	preparajson = '{'
	for z in range(len(arrayRefinado)):
	    dadoEpc = str(arrayRefinado[z].epc)
	    dadoRssi = str(arrayRefinado[z].rssi)
	    dadoTempo = str(arrayRefinado[z].tempo)
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
	con.sendall(bytes(preparajson.encode('utf-8')))
	'''
	a = "b'E20000172211013118905493'"
	b = "b'E20000172211012518905484'"
	preparajson = '{"CARRO0":"'+a+'", "RSSI0":"-44", "TEMPO0":"2021-04-09 20:4'+str(cicloLeitura)+':29.356000", "CARRO1":"'+b+'", "RSSI1":"-44", "TEMPO1":"2021-04-09 20:4'+str(cicloLeitura) +':22.175000", "CicloLeitura":"'+str(cicloLeitura)+'"}\n'
	print (preparajson)
	con.sendall(bytes(preparajson.encode('utf-8')))					

def qualificatorio(con):
	global dadosDaLeitura, tempoQuali, cicloLeitura
	#reader = iniciaLeitor()
	cicloLeitura = 0
	while (tempoQuali>=0):
		#reader.start_reading(lambda tag: dadosLeitura(tag.epc, tag.rssi, datetime.fromtimestamp(tag.timestamp)))
		time.sleep(tempoMin*0.2) # O sensor irá ficar lendo por 20% do tempo minimo de volta
		#reader.stop_reading()
		#time.sleep(tempoMin*0.8) # O sensor irá ficar sem ler por 80% do tempo minimo de volta
		if (tempoQuali==0):
			inicio = timeit.default_timer()
			refinaEnviaDado(cicloLeitura)
			fim = timeit.default_timer()
			time.sleep(10)
			cicloLeitura = cicloLeitura + 1
			tempoQuali = tempoQuali - tempoMin
		else:
			inicio = timeit.default_timer()
			refinaEnviaDado(cicloLeitura)
			fim = timeit.default_timer()
			print ('duracao: %f' % (fim - inicio))
			novoTempo = tempoMin*0.8 - (fim - inicio)
			time.sleep(novoTempo)
			cicloLeitura = cicloLeitura + 1
			tempoQuali = tempoQuali - tempoMin
	print ("acabou o qualificatorio")
	acabouQuali(con)

def acabouQuali(con):
	alerta = '{"URL":"finalQuali", "status":"acabou"}'
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
				dadosCorrida(con, dados)
			elif(dados['URL'] == "retornaEPC"):
				retornaEPC(con)
			elif(dados['URL'] == "comecaQuali"):
				qualificatorio(con)

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
