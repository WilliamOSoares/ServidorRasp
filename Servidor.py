#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
import mercury, time, socket, sys, time, os

cicloLeitura = 1
a = "b'E20000172211013118905493'"
b = "b'E20000172211012518905484'"
print (a)
print (b)
preparajson = '{"CARRO0":"'+a+'", "RSSI0":"-44", "TEMPO0":"2021-04-09 20:4'+str(cicloLeitura)+':29.356000", "CARRO1":"'+b+'", "RSSI1":"-44", "TEMPO1":"2021-04-09 20:4'+str(cicloLeitura) +':22.175000", "CicloLeitura":"'+str(cicloLeitura)+'"}\n'
print (preparajson)