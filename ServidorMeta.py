from __future__ import print_function
from datetime import datetime
from LeituraCarros import leituraCarro
from threading import *
import mercury, time, socket, sys, time, os, json, timeit


mercury.Reader("tmr:///dev/ttyUSB0", baudrate=230400)