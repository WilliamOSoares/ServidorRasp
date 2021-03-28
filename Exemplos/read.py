#!/usr/bin/env python3
import mercury

# configura a leitura na porta serial onde esta o sensor
reader = mercury.Reader("tmr:///dev/ttyUSB0")

# para funcionar use sempre a regiao "NA2" (Americas)
reader.set_region("NA2")

# nao altere a potencia do sinal para nao prejudicar a placa
reader.set_read_plan([1], "GEN2", read_power=1100)

# realiza a leitura das TAGs proximas e imprime na tela
print(reader.read())
