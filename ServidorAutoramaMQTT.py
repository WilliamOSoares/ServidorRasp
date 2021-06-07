'''
//Servidor Autorama com leitor RFID e MQTT//
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
#from thread_botao import Botao
from threading import *
import time, socket, sys, time, os, json, timeit #, mercury
import paho.mqtt.client as mqtt
#import RPi.GPIO as GPIO

'''
* Declarações das variáveis globais que serão alteradas e pegas durante a chamada dos métodos.
'''
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
function = " "
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
clean = "b'"
trava = BoundedSemaphore(1)
online = False # False = pausar as threads, True = continuar as threads
threadInit = True #Lógica inversa (True = não está iniciada)
bt = False # True = se o botão for apertado, False = se não
envia = False # Se for True os dados são enviados
#reader = mercury.Reader("tmr:///dev/ttyUSB0", baudrate=230400) #Inicialização do reader para ele ser um objeto da mercury

'''
* Monitora o estado do botão.
'''
def monitor_botao():
	global bt
	while True:
		input_state = GPIO.input(18)
		if input_state == False:
			bt = True
			print("Botao apertado")
		time.sleep(0.1)

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
def configLeitor():
	global portaSerial, baud, regiao, antena, protocolo, readPower, reader
	#leitor = mercury.Reader(portaSerial, baudrate=baud)
	#leitor.set_region(regiao)
	#leitor.set_read_plan([antena], protocolo, read_power=readPower)
	#reader = leitor
	ret = client.publish("Resposta/Config", "OK", 0)
	print("published return="+str(ret))

'''
* Salva os dados da configuração da corrida e do qualificatório de acordo com os dados fornecidos pelo cliente.
* Como também retorna o status final de execução.
'''
def dadosCorrida():
	global voltas, tempoMin, tempoQuali, length_max
	print("Voltas: "+str(voltas)+" TempoQuali: "+str(tempoQuali)+" TempoMin: "+str(tempoMin)+" QuantiCarros: "+str(length_max))
	ret = client.publish("Resposta/Config", "OK", 0)
	print("published return="+str(ret))

'''
* Método auxiliar chamado pela thread produtora de dados, 
* onde os dados da leitura são colocados em um vetor,
* este vetor tem uma quantidade máxima de corredores e
* dentro desse vetor não pode haver EPCs duplicadas.
'''
def dadosLeitura(epc, rssi, date):
	global dadosDaLeitura, length_max, tempoMin, trava, envia
	trava.acquire()
	verifica = False
	bit = True
	if(len(dadosDaLeitura)==0):
		leitura = leituraCarro(epc, rssi, date)
		dadosDaLeitura.append(leitura)
		envia = True
	elif(len(dadosDaLeitura)>0):
		for x in range(len(dadosDaLeitura)):
			if(dadosDaLeitura[x].epc == epc):
				envia = dadosDaLeitura[x].validaTempo(date, tempoMin)
				if(verifica==False and envia==True):
					verifica = True
				bit = False
		if(bit):
			leitura = leituraCarro(epc, rssi, date)
			dadosDaLeitura.append(leitura)
			envia = True
		if(verifica):
			envia = True
	trava.release()

'''
* Método auxiliar chamado pela thread consumidora de dados,
* Onde é pego os dados do vetor do produtor, com eles,
* é produzido um JSON "manualmente" e preparado para o envio
* para o cliente e logo em seguida, é enviado.
'''
def refinaEnviaDado(cicloLeitura):
	global dadosDaLeitura, bt, trava, envia
	trava.acquire()	
	if(envia):
		if(len(dadosDaLeitura)>0):		
			for z in range(len(dadosDaLeitura)):
				dadoEpc = str(dadosDaLeitura[z].epc)
				topic = dadoEpc
				for i in range(len(topic)):
					for j in range(len(clean)):
						topic =  topic.replace(clean[j], '')
				topico = "LeitorRFID/" + topic
				ret = client.publish(topico4, dadoEpc, 0)
				print("published return="+str(ret))
				dadoRssi = str(dadosDaLeitura[z].rssi)
				dadoTempo = str(dadosDaLeitura[z].tempo)
				topico2 = "LeitorRFID/" + topic + "/Tempo"
				ret = client.publish(topico2, dadoTempo, 0)
				print("published return="+str(ret))
				topico3 = "LeitorRFID/" + topic + "/Rssi"
				ret = client.publish(topico3, dadoRssi, 0)
				print("published return="+str(ret))
				topico4 = "LeitorRFID/" + topic + "/Ciclo"
				ret = client.publish(topico4, str(cicloLeitura), 0)
				print("published return="+str(ret))
				
		dadosDaLeitura = []
		if (bt):
			topico5 = "Config/Botao"
			ret = client.publish(topico5, str(bt), 0)
			print("published return="+str(ret))
			bt = False
		envia = False
		trava.release()
		return True
	else:
		trava.release()
		return False

'''
* Thead Consumidora, que monta o JSON e envia para o cliente.
'''
def consumidor():
	global dadosDaLeitura, tempoQuali, cicloLeitura, trava, online
	while True:	
		while online:
			if(refinaEnviaDado(cicloLeitura)):
					cicloLeitura+=1

'''
* Método de iniciar as threads depois de criadas, mas deixando paradas.
'''
def iniciaThread():
	global threadInit
	consumidor.start()
	threadInit = False

'''
* Método do qualificatorio, onde as 2 threads são acordas até o tempo do qualificatório
* fornecido pelo cliente acabar, após o término do tempo, as 2 threads são colocas para 
* dormir e é enviado ao cliente que o qualificatório acabou. 
'''
def qualificatorio(consumidor):
	global dadosDaLeitura, tempoQuali, cicloLeitura, trava, online, bt, envia
	reader = iniciaLeitor()
	cicloLeitura = 0
	tempo = tempoQuali
	time.sleep(5)
	reader.start_reading(lambda tag: dadosLeitura(tag.epc, tag.rssi, datetime.fromtimestamp(tag.timestamp)))
	online = True
	ini = time.time()
	while (tempo>0):
		time.sleep(5)
		print(bt)
		fim = time.time()
		if ((fim-ini)>=tempo):
			tempo=0
			reader.stop_reading()
		print (fim-ini)	
	if (tempo==0):
		time.sleep(1)
	trava.acquire()
	online = False
	trava.release()
	dadosDaLeitura = []
	envia = False
	print ("acabou o qualificatorio")
	ret = client.publish("Resposta/Quali", "Acabou", 0)
	print("published return="+str(ret))

'''
* Método que retorna os EPCs da tags existentes para o cliente.
* Deve haver no mínimo 1 tag abaixo do leitor.
'''
def retornaEPC():
	global clean
	'''
	reader = iniciaLeitor()
	tags = list(map(lambda t: t.epc, reader.read()))
	for x in range(len(tags)):
		dado = str(tags[x])
		topic = dado
		for i in range(len(topic)):
			for j in range(len(clean)):
				topic =  topic.replace(clean[j], '')
		topico = "LeitorRFID/" + topic
		ret = client.publish(topico, dado, 1)
		print("published return="+str(ret))
	ret = client.publish("Resposta/Config", "EPC", 1)
	print("published return="+str(ret))
	'''
	epc1 = "b'E2000017221101241890547C'"
	epc2 = "b'E20000172211012518905484'"
	epc3 = "b'E20000172211013118905493'"
	topic1= epc1
	topic2= epc2
	topic3= epc3
	for i in range(len(topic1)):
		for j in range(len(clean)):
			topic1 =  topic1.replace(clean[j], '')
	topico = "LeitorRFID/" + topic1
	ret = client.publish(topico, epc1, 0)
	print("published return="+str(ret))
	for i in range(len(topic2)):
		for j in range(len(clean)):
			topic2 =  topic2.replace(clean[j], '')
	topico = "LeitorRFID/" + topic2
	ret = client.publish(topico, epc2, 0)
	print("published return="+str(ret))
	for i in range(len(topic3)):
		for j in range(len(clean)):
			topic3 =  topic3.replace(clean[j], '')
	topico = "LeitorRFID/" + topic3
	ret = client.publish(topico, epc3, 0)
	print("published return="+str(ret))
	ret = client.publish("Resposta/Config", "EPC", 0)
	print("published return="+str(ret))

'''
* Método da corrida, onde as 2 threads são acordas até o tempo mínimo de volta + 10 segundos
* multiplicado pelo número de voltas acabar, após o término do tempo, as 2 threads são colocas 
* para dormir e é enviado ao cliente que a corrida acabou. 
'''
def corrida(consumidor):
	global dadosDaLeitura, tempoMin, cicloLeitura, trava, online, voltas
	reader = iniciaLeitor()
	cicloLeitura = 0
	time.sleep(5)
	reader.start_reading(lambda tag: dadosLeitura(tag.epc, tag.rssi, datetime.fromtimestamp(tag.timestamp)))
	online = True
	tempoCorrida = ((tempoMin*60)+10)*voltas
	ini = time.time()
	while (tempoCorrida>0):
		time.sleep(5)
		fim = time.time()
		if ((fim-ini)>=tempoCorrida):
			tempoCorrida=0
			reader.stop_reading()
		print (fim-ini)	
	if (tempoCorrida==0):
		time.sleep(5)
	trava.acquire()
	online = False
	trava.release()	
	dadosDaLeitura = []
	envia = False
	print ("acabou a corrida")
	ret = client.publish("Resposta/Corrida", "Acabou", 0)
	print("published return="+str(ret))

'''
* Método que repassa para os demais métodos qual tipo de ação que o cliente deseja executar.
'''
def atende(consumidor):
	global threadInit, function
	print ('Iniciando...')
	print (function)
	if(function == "ConfigLeitor"):
		configLeitor()
	elif(function == "DadosCorrida"):
		dadosCorrida()
	elif(function == "PegaEPC"):
		retornaEPC()
	elif(function == "ComecaQuali"):
		ret = client.publish("Resposta/Quali", "OK", 0)
		print("published return="+str(ret))
		simulaQuali()
		'''
		if(threadInit):
			iniciaThread()
		qualificatorio(consumidor)
		'''
	elif(function == "ComecaCorrida"):
		ret = client.publish("Resposta/Corrida", "OK", 0)
		print("published return="+str(ret))
		simulaCorrida()
		#corrida(consumidor)
	print ('requisição finalizada!')

'''
* Início de execução do código, onde é definido quais métodos serão threads, 
* onde é feito a conexão com o cliente, onde também é atendido todas as requisições do cliente.
'''

'''
* Se inscreve em um tópico na conexão.
'''
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe("ConfigLeitor/#")
	client.subscribe("Function/#")
	client.subscribe("Config/#")

'''
* Recebe todas as mensagens.
'''
def on_message(client, userdata, msg):
	global portaSerial, baud, regiao, antena, protocolo, readPower, function, voltas, tempoMin, tempoQuali, length_max
	print(msg.topic+" "+msg.payload.decode("utf-8"))

	if(msg.topic == "ConfigLeitor/ForcaLeitura"):
		readPower =  int(msg.payload.decode("utf-8"))
	elif(msg.topic == "ConfigLeitor/Protocolo"):
		protocolo =  msg.payload.decode("utf-8")
	elif(msg.topic == "ConfigLeitor/Antena"):
		antena =  int(msg.payload.decode("utf-8"))
	elif(msg.topic == "ConfigLeitor/Regiao"):
		regiao =  msg.payload.decode("utf-8")
	elif(msg.topic == "ConfigLeitor/Baudrate"):
		baudrate = int(msg.payload.decode("utf-8"))
	elif(msg.topic == "ConfigLeitor/Serial"):
		portaSerial =  msg.payload.decode("utf-8")
	elif(msg.topic == "Config/TempoQuali"): 
		tempoQuali = int(msg.payload.decode("utf-8"))*60
	elif(msg.topic == "Config/NumeroVoltas"):
		voltas = int(msg.payload.decode("utf-8"))
	elif(msg.topic == "Config/TempoMinimo"):
		tempoMin = int(msg.payload.decode("utf-8"))*60
	elif(msg.topic == "Config/QuantiCarros"): 
		length_max = int(msg.payload.decode("utf-8"))	
	elif(msg.topic == "Function"): #tem que chamar a função aqui
		function = msg.payload.decode("utf-8")
		
consumidor = Thread(target=consumidor)
#botao = Thread(target=monitor_botao)
client = mqtt.Client("williamsoares@ecomp.uefs.br", False)
client.username_pw_set("williamw0nka", "sDuXCugk-6xD9Og9d")
client.on_connect = on_connect
client.on_message = on_message

client.connect("node02.myqtthub.com", 1883, 60)
client.loop_start()
#botao.start()
print("Entrando no while")
while 1:
	if(not(function == " ")):
		atende(consumidor)
		print("Operação finalizada")
		function = " "

#fim :)

def simulaQuali():
	global dadosDaLeitura, tempoQuali, cicloLeitura
	cicloLeitura = 0
	tempo = tempoQuali
	time.sleep(5)
	ini = time.time()
	while (tempo>0):		
		cicloLeitura = cicloLeitura+1
		fim = time.time()
		if ((fim-ini)>=tempo):
			tempo=0
		print (fim-ini)
		epc1 = "b'E2000017221101241890547C'"
		epc2 = "b'E20000172211012518905484'"
		epc3 = "b'E20000172211013118905493'"
		tempo1 = "2021-04-27 20:"+str(cicloLeitura)+":54.622000"
		tempo2 = "2021-04-27 20:"+str(cicloLeitura+1)+":54.622000"
		tempo3 = "2021-04-27 20:"+str(cicloLeitura+2)+":54.622000"
		if(cicloLeitura<=7):
			tempo1 = "2021-04-27 20:0"+str(cicloLeitura)+":54.622000"
			tempo2 = "2021-04-27 20:0"+str(cicloLeitura+1)+":54.622000"
			tempo3 = "2021-04-27 20:0"+str(cicloLeitura+2)+":54.622000"
		elif(cicloLeitura==8):
			tempo1 = "2021-04-27 20:0"+str(cicloLeitura)+":54.622000"
			tempo2 = "2021-04-27 20:0"+str(cicloLeitura+1)+":54.622000"
			tempo3 = "2021-04-27 20:"+str(cicloLeitura+2)+":54.622000"
		elif(cicloLeitura==9):
			tempo1 = "2021-04-27 20:0"+str(cicloLeitura)+":54.622000"
			tempo2 = "2021-04-27 20:"+str(cicloLeitura+1)+":54.622000"
			tempo3 = "2021-04-27 20:"+str(cicloLeitura+2)+":54.622000"
		topic1= epc1
		topic2= epc2
		topic3= epc3
		for i in range(len(topic1)):
			for j in range(len(clean)):
				topic1 =  topic1.replace(clean[j], '')
		topico = "LeitorRFID/" + topic1
		ret = client.publish(topico, epc1, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic1 + "/Tempo"
		ret = client.publish(topico, tempo1, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic1 + "/Rssi"
		ret = client.publish(topico, cicloLeitura*2, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic1 + "/Ciclo"
		ret = client.publish(topico, str(cicloLeitura), 0)
		print("published return="+str(ret))	
		for i in range(len(topic2)):
			for j in range(len(clean)):
				topic2 =  topic2.replace(clean[j], '')
		topico = "LeitorRFID/" + topic2
		ret = client.publish(topico, epc2, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic2 + "/Tempo"
		ret = client.publish(topico, tempo2, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic2 + "/Rssi"
		ret = client.publish(topico, cicloLeitura*2, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic2 + "/Ciclo"
		ret = client.publish(topico, str(cicloLeitura), 0)
		print("published return="+str(ret))	
		for i in range(len(topic3)):
			for j in range(len(clean)):
				topic3 =  topic3.replace(clean[j], '')
		topico = "LeitorRFID/" + topic3
		ret = client.publish(topico, epc3, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic3 + "/Tempo"
		ret = client.publish(topico, tempo3, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic3 + "/Rssi"
		ret = client.publish(topico, cicloLeitura*2, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic3 + "/Ciclo"
		ret = client.publish(topico, str(cicloLeitura), 0)
		print("published return="+str(ret))		
		time.sleep(5)
	if (tempo==0):
		time.sleep(5)
	print ("acabou o qualificatorio")
	ret = client.publish("Resposta/Quali", "Acabou", 0)
	print("published return="+str(ret))

def simulaCorrida():
	global dadosDaLeitura, tempoQuali, cicloLeitura, voltas
	cicloLeitura = 0
	time.sleep(5)
	tempoCorrida = (tempoQuali+10)*voltas
	ini = time.time()
	while (tempoCorrida>0):
		cicloLeitura = cicloLeitura+1
		fim = time.time()
		if ((fim-ini)>=tempoCorrida):
			tempoCorrida=0
		print (fim-ini)	
		epc1 = "b'E2000017221101241890547C'"
		epc2 = "b'E20000172211012518905484'"
		epc3 = "b'E20000172211013118905493'"
		tempo1 = "2021-04-27 20:"+str(cicloLeitura)+":54.622000"
		tempo2 = "2021-04-27 20:"+str(cicloLeitura+1)+":54.622000"
		tempo3 = "2021-04-27 20:"+str(cicloLeitura+2)+":54.622000"
		if(cicloLeitura<=7):
			tempo1 = "2021-04-27 20:0"+str(cicloLeitura)+":54.622000"
			tempo2 = "2021-04-27 20:0"+str(cicloLeitura+1)+":54.622000"
			tempo3 = "2021-04-27 20:0"+str(cicloLeitura+2)+":54.622000"
		elif(cicloLeitura==8):
			tempo1 = "2021-04-27 20:0"+str(cicloLeitura)+":54.622000"
			tempo2 = "2021-04-27 20:0"+str(cicloLeitura+1)+":54.622000"
			tempo3 = "2021-04-27 20:"+str(cicloLeitura+2)+":54.622000"
		elif(cicloLeitura==9):
			tempo1 = "2021-04-27 20:0"+str(cicloLeitura)+":54.622000"
			tempo2 = "2021-04-27 20:"+str(cicloLeitura+1)+":54.622000"
			tempo3 = "2021-04-27 20:"+str(cicloLeitura+2)+":54.622000"
		topic1= epc1
		topic2= epc2
		topic3= epc3
		for i in range(len(topic1)):
			for j in range(len(clean)):
				topic1 =  topic1.replace(clean[j], '')
		topico = "LeitorRFID/" + topic1
		ret = client.publish(topico, epc1, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic1 + "/Tempo"
		ret = client.publish(topico, tempo1, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic1 + "/Rssi"
		ret = client.publish(topico, cicloLeitura*2, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic1 + "/Ciclo"
		ret = client.publish(topico, str(cicloLeitura), 0)
		print("published return="+str(ret))	
		for i in range(len(topic2)):
			for j in range(len(clean)):
				topic2 =  topic2.replace(clean[j], '')
		topico = "LeitorRFID/" + topic2
		ret = client.publish(topico, epc2, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic2 + "/Tempo"
		ret = client.publish(topico, tempo2, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic2 + "/Rssi"
		ret = client.publish(topico, cicloLeitura*2, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic2 + "/Ciclo"
		ret = client.publish(topico, str(cicloLeitura), 0)
		print("published return="+str(ret))	
		for i in range(len(topic3)):
			for j in range(len(clean)):
				topic3 =  topic3.replace(clean[j], '')
		topico = "LeitorRFID/" + topic3
		ret = client.publish(topico, epc3, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic3 + "/Tempo"
		ret = client.publish(topico, tempo3, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic3 + "/Rssi"
		ret = client.publish(topico, cicloLeitura*2, 0)
		print("published return="+str(ret))
		topico = "LeitorRFID/" + topic3 + "/Ciclo"
		ret = client.publish(topico, str(cicloLeitura), 0)
		print("published return="+str(ret))		
		time.sleep(5)
	if (tempoCorrida==0):
		time.sleep(5)
	print ("acabou a corrida")
	ret = client.publish("Resposta/Corrida", "Acabou", 0)
	print("published return="+str(ret))