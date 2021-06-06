#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime, timedelta
import time, socket, sys, time, os, json #, mercury

class leituraCarro:

	def __init__(self, epc, rssi,tempo):
		self.epc = epc
		self.rssi = rssi
		self.tempo = tempo

	def setEPC(self, epc):
		self.epc = epc

	def setRSSI(self, rssi):
		self.rssi = rssi

	def setTempo(self, tempo):
		self.tempo = tempo

	def validaTempo(self, novoTempo, tempoMin):
		tempoAtual = str(self.tempo) 
		tempoNovo = str(novoTempo)
		if(not("." in tempoNovo)):
			if(not("." in tempoAtual)):
				a = tempoAtual.split(" ")
				b = a[1].split(":")
				delta = timedelta(hours=int(b[0]),minutes=int(b[1]),seconds=int(b[2]),milliseconds=000)
				s = tempoNovo.split(" ")
				t = s[1].split(":")
				delta2 = timedelta(hours=int(t[0]),minutes=int(t[1]),seconds=int(t[2]),milliseconds=000)
				result = delta2-delta
				compara = timedelta(hours=0,minutes=int(tempoMin),seconds=0,milliseconds=000)
				if(result>compara):
					self.setTempo(novoTempo)
					return True
				else:
					return False
			else:
				s = tempoAtual.split(" ")
				t = s[1].split(":")
				u = t[2].split(".")
				v = u[1]
				v = v[:len(v) - 3]
				delta = timedelta(hours=int(t[0]),minutes=int(t[1]),seconds=int(u[0]),milliseconds=int(v))
				a = tempoNovo.split(" ")
				b = a[1].split(":")
				delta2 = timedelta(hours=int(b[0]),minutes=int(b[1]),seconds=int(b[2]),milliseconds=000)
				result = delta2-delta
				compara = timedelta(hours=0,minutes=int(tempoMin),seconds=0,milliseconds=000)
				if(result>compara):
					self.setTempo(novoTempo)
					return True
				else:
					return False
		else:
			if(not("." in tempoAtual)):
				a = tempoAtual.split(" ")
				b = a[1].split(":")
				delta = timedelta(hours=int(b[0]),minutes=int(b[1]),seconds=int(b[2]),milliseconds=000)
				s = tempoNovo.split(" ")
				t = s[1].split(":")
				u = t[2].split(".")
				v = u[1]
				v = v[:len(v) - 3]
				delta2 = timedelta(hours=int(t[0]),minutes=int(t[1]),seconds=int(u[0]),milliseconds=int(v))
				result = delta2-delta
				compara = timedelta(hours=0,minutes=int(tempoMin),seconds=0,milliseconds=000)
				if(result>compara):
					self.setTempo(novoTempo)
					return True
				else:
					return False
			else:
				s = tempoAtual.split(" ")
				t = s[1].split(":")
				u = t[2].split(".")
				v = u[1]
				v = v[:len(v) - 3]
				delta = timedelta(hours=int(t[0]),minutes=int(t[1]),seconds=int(u[0]),milliseconds=int(v))
				a = tempoNovo.split(" ")
				b = a[1].split(":")
				c = b[2].split(".")
				d = c[1]
				d = d[:len(d) - 3]
				delta2 = timedelta(hours=int(b[0]),minutes=int(b[1]),seconds=int(c[0]),milliseconds=int(d))
				result = delta2-delta
				compara = timedelta(hours=0,minutes=int(tempoMin),seconds=0,milliseconds=000)
				if(result>compara):
					self.setTempo(novoTempo)
					return True
				else:
					return False