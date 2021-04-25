'''
//Servidor Autorama com leitor RFID//
/*******************************************************************************
Autores: Víctor César da Rocha Bastos e William Oliveira Soares
Componente Curricular: MI de Concorrência e Conectividade
Concluido em: 25/04/2021
Declaro que este código foi elaborado por nós de forma coletiva e não contém nenhum
trecho de código de outro colega ou de outro autor, tais como provindos de livros e
apostilas, e páginas ou documentos eletrônicos da Internet. Qualquer trecho de código
de outra autoria que não seja a nossa está destacado com uma citação para o autor e a fonte
do código, e estou ciente que estes trechos não serão considerados para fins de avaliação.
***************************************************************************************/
'''
#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
from LeituraCarros import leituraCarro
from threading import *
import mercury, time, socket, sys, time, os, json, timeit
'''
* Declarações das variáveis globais que serão alteradas e pegas durante a chamada dos métodos.
'''
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
online = False # False = pausar as threads, True = continuar as threads
threadInit = True #Lógica inversa (True = não está iniciada)
conectado = True #Lógica inversa (True = cliente não conectado)
reader = mercury.Reader("tmr:///dev/ttyUSB0", baudrate=230400) #Inicialização do reader para ele ser um objeto da mercury

'''
* Inicia o leitor com as configurações fornecidas pelo cliente.
'''
def iniciaLeitor():
	global portaSerial, baud, regiao, antena, protocolo, readPower
	reader = mercury.Reader(portaSerial, baudrate=baud)
	reader.set_region(regiao)
	reader.set_read_plan([antena], protocolo, read_power=readPower)
	return reader

'''
* Salva os dados da configuração do leitor de acordo com os dados fornecidos pelo cliente.
* Como também retorna o status final de execução.
'''
def configLeitor(con, arqJson):
	global portaSerial, baud, regiao, antena, protocolo, readPower, conectado
	portaSerial = arqJson['portaSerial']
	baud = int(arqJson['baudrate'])
	regiao = arqJson['regiao']
	antena = int(arqJson['antena'])
	protocolo = arqJson['protocolo']
	readPower = int(arqJson['power'])
	mensagem = '{"URL":"configLeitor", "return":"OK"}'
	preparacaoEnvio = mensagem + "\n"
	try:
		con.sendall(bytes(preparacaoEnvio.encode('utf-8')))
	except (socket.error):
		conectado = True
		print ("Conexão perdida")

'''
* Salva os dados da configuração da corrida e do qualificatório de acordo com os dados fornecidos pelo cliente.
* Como também retorna o status final de execução.
'''
def dadosCorrida(con, arqJson):
	global voltas, tempoMin, tempoQuali, length_max, conectado
	voltas = int(arqJson['Voltas'])
	tempoQuali = int(arqJson['Quali'])*60
	tempoMin = int(arqJson['TempoMin'])*60
	mensagem = '{"URL":"dadosCorrida", "return":"OK"}'
	length_max = int(arqJson['CarrosQuant'])
	preparacaoEnvio = mensagem + "\n"
	try:
		con.sendall(bytes(preparacaoEnvio.encode('utf-8')))
	except (socket.error):
		conectado = True
		print ("Conexão perdida")

'''
* Método auxiliar chamado pela thread produtora de dados, 
* onde os dados da leitura são colocados em um vetor,
* este vetor tem uma quantidade máxima de corredores e
* dentro desse vetor não pode haver EPCs duplicadas.
'''
def dadosLeitura(epc, rssi, date):
	global dadosDaLeitura, length_max
	bit = True
	if(len(dadosDaLeitura)==0):
		leitura = leituraCarro(epc, rssi, date)
		dadosDaLeitura.append(leitura)
	elif(len(dadosDaLeitura)<length_max):
		for x in range(len(dadosDaLeitura)):
			if(dadosDaLeitura[x].epc == epc):
				bit = False
		if(bit):
			leitura = leituraCarro(epc, rssi, date)
			dadosDaLeitura.append(leitura)

'''
* Método auxiliar chamado pela thread consumidora de dados,
* Onde é pego os dados do vetor do produtor, com eles,
* é produzido um JSON "manualmente" e preparado para o envio
* para o cliente e logo em seguida, é enviado.
'''
def refinaEnviaDado(cicloLeitura):
	global dadosDaLeitura, conectado
	if(len(dadosDaLeitura)>0):		
		preparajson = '{'
		for z in range(len(dadosDaLeitura)):
		    dadoEpc = str(dadosDaLeitura[z].epc)
		    dadoRssi = str(dadosDaLeitura[z].rssi)
		    dadoTempo = str(dadosDaLeitura[z].tempo)
		    preparajson = preparajson + '"CARRO'+str(z)+ '":"' + dadoEpc + '", "RSSI'+str(z)+ '":"' + dadoRssi + '", "TEMPO'+str(z)+ '":"' + dadoTempo + '", '
		preparajson = preparajson + '"CicloLeitura":"' + str(cicloLeitura) + '", '
		size = len(preparajson)
		remove = preparajson[:size - 2]
		preparajson = remove
		preparajson = preparajson +'}'
		preparajson = preparajson +	"\n"
		print(preparajson)
		dadosDaLeitura = []
		try:
			con.sendall(bytes(preparajson.encode('utf-8')))
		except (socket.error):
			conectado = True
			print ("Conexão perdida")
		return True
	else:
		return False

'''
* Thread produtora, que faz leituras constante das tags com o leitor RFID.
'''
def produtor():
	global dadosDaLeitura, tempoQuali, cicloLeitura, trava, online, reader
	while True:	
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

'''
* Thead produtora, que monta o JSON e envia para o cliente.
'''
def consumidor():
	global dadosDaLeitura, tempoQuali, cicloLeitura, trava, online
	while True:	
		while online:
			print("consumindo")
			trava.acquire()	
			print("consumindo travado")
			if(online):
				if(refinaEnviaDado(cicloLeitura)):
					cicloLeitura+=1
			trava.release()

'''
* Método de iniciar as threads depois de criadas, mas deixando paradas.
'''
def iniciaThread():
	global threadInit
	produtor.start()
	consumidor.start()
	threadInit = False

'''
* Método do qualificatorio, onde as 2 threads são acordas até o tempo do qualificatório
* fornecido pelo cliente acabar, após o término do tempo, as 2 threads são colocas para 
* dormir e é enviado ao cliente que o qualificatório acabou. 
'''
def qualificatorio(con, produtor, consumidor):
	global dadosDaLeitura, tempoQuali, cicloLeitura, trava, online, conectado
	reader = iniciaLeitor()
	cicloLeitura = 0
	tempo = tempoQuali
	time.sleep(5)
	online = True
	ini = time.time()
	while (tempo>0):
		time.sleep(5)
		fim = time.time()
		if ((fim-ini)>=tempo):
			tempo=0
		print (fim-ini)	
		if (conectado):
			trava.acquire()
			online = False
			trava.release()
			tempo=0
	if (tempo==0):
		time.sleep(5)
	trava.acquire()
	online = False
	trava.release()
	print ("acabou o qualificatorio")
	alerta = '{"URL":"finalQuali", "status":"acabou", "CicloLeitura":"' + str(cicloLeitura) + '"}'
	preparacaoEnvio = alerta + "\n"
	print (preparacaoEnvio)
	try:
		con.sendall(bytes(preparacaoEnvio.encode('utf-8')))
	except (socket.error):
		conectado = True
		print ("Conexão perdida")

'''
* Método que retorna os EPCs da tags existentes para o cliente.
* Deve haver no mínimo 1 tag abaixo do leitor.
'''
def retornaEPC(con):
	global conectado
	reader = iniciaLeitor()
	tags = list(map(lambda t: t.epc, reader.read()))
	preparajson = '{'
	for x in range(len(tags)):
	    dado = str(tags[x])
	    preparajson = preparajson + '"EPC'+str(x)+ '":"' + dado + '", '
	
	size = len(preparajson)
	remove = preparajson[:size - 2]
	preparajson = remove
	preparajson = preparajson +'}'
	preparajson = preparajson +	"\n"
	print(preparajson)
	try:
		con.sendall(bytes(preparajson.encode('utf-8')))
	except (socket.error):
		conectado = True
		print ("Conexão perdida")

'''
* Método da corrida, onde as 2 threads são acordas até o tempo mínimo de volta + 10 segundos
* multiplicado pelo número de voltas acabar, após o término do tempo, as 2 threads são colocas 
* para dormir e é enviado ao cliente que a corrida acabou. 
'''
def corrida(con, produtor, consumidor):
	global dadosDaLeitura, tempoMin, cicloLeitura, trava, online, voltas, conectado
	reader = iniciaLeitor()
	cicloLeitura = 0
	time.sleep(5)
	online = True
	tempoCorrida = (tempoMin+10)*voltas
	ini = time.time()
	while (tempoCorrida>0):
		time.sleep(5)
		fim = time.time()
		if ((fim-ini)>=tempoCorrida):
			tempoCorrida=0
		print (fim-ini)	
		if (conectado):
			trava.acquire()
			online = False
			trava.release()
			tempoCorrida=0
	if (tempoCorrida==0):
		time.sleep(5)
	trava.acquire()
	online = False
	trava.release()
	print ("acabou a corrida")
	alerta = '{"URL":"finalCorrida", "status":"acabou", "CicloLeitura":"' + str(cicloLeitura) + '"}'
	preparacaoEnvio = alerta + "\n"
	print (preparacaoEnvio)
	try:
		con.sendall(bytes(preparacaoEnvio.encode('utf-8')))
	except (socket.error):
		conectado = True
		print ("Conexão perdida")

'''
* Método que repassa para os demais métodos qual tipo de ação que o cliente deseja executar.
'''
def atende(con, produtor, consumidor):
	global threadInit, conectado
	print ('Iniciando...')
	try:
		recb = con.recv(1024).decode('utf-8')
	except (socket.error):
		if (conectado):
			print ("Conexão finalizada")
		else:
			conectado = True
			print ("Conexão perdida")
	if (not(conectado)):
		print (recb)
		dados = json.loads(recb)
		if(dados['METODO'] == "POST"):
			if(dados['URL'] == "configLeitor"):
				configLeitor(con, dados)
			elif(dados['URL'] == "encerra"):
				encerraConexao(con)
		elif(dados['METODO'] == "GET"):
			if(dados['URL'] == "dadosCorrida"):
				dadosCorrida(con, dados)
			elif(dados['URL'] == "retornaEPC"):
				retornaEPC(con)
			elif(dados['URL'] == "comecaQuali"):
				if(threadInit):
					iniciaThread();
				qualificatorio(con, produtor, consumidor)
			elif(dados['URL'] == "comecaCorrida"):
				corrida(con, produtor, consumidor)
			else:
				print("Não é um POST e nem um GET")
		print ('requisição finalizada!')
'''
* Conecta com o proximo cliente.
'''
def conectarCliente(s):
	global conectado, con, cliente
	conectado = False
	s.listen(1)
	con, cliente = s.accept()
	print ('Concetado por', cliente)

'''
* Encerra conexão com o cliente.
'''
def encerraConexao(con):
	global conectado
	print ('Finalizando conexao do cliente')
	con.close()
	conectado = True

'''
* Início de execução do código, onde é definido quais métodos serão threads, 
* onde é feito a conexão com o cliente, onde também é atendido todas as requisições do cliente.
'''
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
conectado = False

while 1:
	try:
		if(conectado):
			conectarCliente(s)
		else:
			atende(con, produtor, consumidor)	
	except (socket.error):
		if (conectado):
			print ("Conexão finalizada")
		else:
			print ("Conexão perdida")
		conectado = True
		online = False
		voltas = 0
		tempoMin = 0
		tempoQuali = 0
		dadosDaLeitura = []
		cicloLeitura = 0
		length_max = 0
		online = False
		threadInit = True
		conectado = True

#fim :)