#!/usr/bin/env python3

from threading import Thread
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class Botao:
    def __init__(self):
        self.estado = False

    def setEstado(self, estado):
        self.estado = estado

    def getEstado(self):
        return self.estado

bt = Botao()

def monitor_botao():
	while True:
		input_state = GPIO.input(18)
		if input_state == False:
			bt.setEstado(True)
			return
		time.sleep(0.1)


if __name__ == "__main__":

	apertos = 0
	bt.setEstado(False)
	thread_botao = Thread(target=monitor_botao)
	thread_botao.start()
	print("Esperando apertar o botao 5 vezes para sair:")
	while True:
		if bt.getEstado() == True:
			apertos +=1
			print("Botao acionado "+str(apertos)+" vezes." )
			bt.setEstado(False)
			thread_botao = Thread(target=monitor_botao)
			thread_botao.start()
		if apertos > 4: 
			print("O botao foi apertado 5 vezes: saindo do programa.")
			quit()
		time.sleep(0.2)

