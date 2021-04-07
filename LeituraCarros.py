#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
import mercury, time, socket, sys, time, os, json

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