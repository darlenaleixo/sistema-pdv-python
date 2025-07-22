import escpos
import os

# Encontra o diretório onde a biblioteca escpos está instalada
escpos_path = os.path.dirname(escpos.__file__)
print(escpos_path)