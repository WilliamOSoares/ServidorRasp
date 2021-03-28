# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from __future__ import print_function
import time
from datetime import datetime
import mercury

# configuracao basica para uma primeira leitura sobre o leitor RFID: porta serial e taxa de transmissão 
reader = mercury.Reader("tmr:///dev/ttyUSB0", baudrate=230400)

#  agora vamos solicitar informacoes sobre o leitor RFID para configura-lo corretamente
print("informacoes  sobre o leitor:")

# imprime o modelo do sensor
print(reader.get_model())

# imprime as regioes compativeis 
print(reader.get_supported_regions())

# imprime as antenas disponiveis.
# perceba que só existe a antena [1] no leitor
print(reader.get_antennas())

# imprime o intervalo de possiveis potencias
# ATENCAO: nao ultrapasse o limite maximo
print(reader.get_power_range())

# imprime a temperatura do sensor
print(reader.get_temperature())

# configuracao do plano de leitura
# obs.: com a potencia em 1500 (15db) este leitor trabalha melhor
reader.set_region("NA2")
reader.set_read_plan([1], "GEN2", read_power=1500)

# realiza uma leitura do sensor 
print(reader.read())

# inicia leituras repetidas sobre o sensor (sempre que passa uma tag)
# a funcao START_READING recebe como parametro outra funcao (callback)  
# funcao callback eh chamada para tratar resulto de cada leitura (tag)
# No caso abaixo, a funcao LAMBDA do python para imprimir campos da tag
reader.start_reading(lambda tag: print(tag.epc, tag.antenna, tag.read_count, tag.rssi, datetime.fromtimestamp(tag.timestamp)))

# processo espera por um segundo (deixa o processo fazendo leituras)
time.sleep(1)

# para de realizar leituras repetidas sobre o leitor
reader.stop_reading()

