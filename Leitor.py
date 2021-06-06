#!/usr/bin/env python3
from __future__ import print_function
import time
from datetime import datetime
#import mercury

# An extremely simple HTTP server
import socket, sys, time, os
# Server runs on all IP addresses by default

epc1 = "b'E2000017221101241890547C'"
clean = "b'"
for i in range(len(epc1)):
	for j in range(len(clean)):
		epc1 =  epc1.replace(clean[j], '')

print(epc1)

sys.exit(-1)



