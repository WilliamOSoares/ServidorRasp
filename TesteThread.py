#!/usr/bin/env python3

from threading import *
from random import randint
import time
import sys
import os

lista = [] #cria uma lista de valores com nenhum valor inserido
length_max = 4 #tamanho max do vetor
trava = BoundedSemaphore(1)
online = True

#Processo A (produtor), produz valores para a lista
def produtor():
	global lista, length_max, trava, online

	while online:
		while len(lista) < length_max: #verifica se a lista não atingiu seu tamanho máximo
			trava.acquire()
			lista.append(randint(0, 1000)) #adiciona um valor inteiro entre 0 e 1000 à lista
			print ('Olá Sr. Programador eu sou o produtor, olha como está a lista de valores ' + str(lista))
			trava.release()
		else:
			print ('Fiz o meu serviço olha como eu deixei a lista cheinha >>> ' + str(lista))
			print ('Agora eu vou tirar uma soneca. [Produtor está tirando uma soneca acorde ele quando a lista estiver vazia] \n')
		

#Processo B (consumidor), consome valores da lista      
def consumidor():
	global lista, length_max, dormir_c, dormir_p, trava, online

	while online:
		if lista: #verifica se a lista contem valores
			trava.acquire()
			del lista[0] #remove o valor que se encontra no inicio da lista
			print ('Olá Sr. Programador eu sou o consumidor, olha como está a lista de valores' + str(lista))
			trava.release()
		else:
			print ('Fiz o meu serviço olha como eu deixei a lista limpinha >>> ' + str(lista))
			print ('Agora eu vou tirar uma soneca. [Consumidor está tirando uma soneca, acorde ele quando a lista possuir valores] \n')
		

produtor = Thread(target=produtor)
consumidor = Thread(target=consumidor)
produtor.start()
consumidor.start()
time.sleep(1)
online = False