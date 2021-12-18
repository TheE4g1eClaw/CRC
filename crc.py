from numpy import array, random
from numpy.random import bit_generator
from bitarray import bitarray
import threading

def cyclic_redundancy_check(filename: str, divisor: str, len_crc: int) -> int:
    """
    This function computes the CRC of a plain-text file 
    arguments:
    filename: the file containing the plain-text
    divisor: the generator polynomium
    len_crc: The number of redundant bits (r)
    """
    from bitarray import bitarray
    redundancy = len_crc * bitarray('0')
    bin_file = bitarray()
    p = bitarray(divisor)
    len_p = len(p)
    with open(filename, 'rb') as file:
        bin_file.fromfile(file)         #Codigo original

    cw = bin_file + redundancy          #<- Bin + redundancia de protección
    rem = cw[0 : len_p]                 #<- Residuo de la división // La longitud del residuo es igual a la del divisor
    end = len(cw)
    #División con XOR 
    for i in range(len_p, end + 1):
        if rem[0]:
            rem ^= p
        if i < end:
            rem = rem << 1 
            rem[-1] = cw[i]             
    rem = rem[len_p-len_crc : len_p]    #rem = CRC
    print("Codigo CRC:",rem)
    rem = bin_file + rem                #Concatenamos el codigo original y el CRC
    return rem
        
"""
Prueba del funcionamiento de la función cyclic_redundacy_check
http://www.sunshine2k.de/coding/javascript/crc/crc_js.html
"""
#Implementado
def decoder(divisor:str, code:int, len_crc: int) ->int:
    d = bitarray(divisor)
    len_d = len(d)
    rem = code[0 : len_d]
    end = len(code)
    #División con XOR 
    for i in range(len_d, end + 1):
        if rem[0]:
            rem ^= d
        if i < end:
            rem = rem << 1 
            rem[-1] = code[i]
    #print("Valor descodificado: ",rem)#[len_d-len_crc : len_d])
    retvalue = rem[len_d-len_crc : len_d]
    return retvalue

#Implementado
def generadorErrores(code:int, nErrores:int, semilla):
    from numpy.random import Generator, MT19937, SeedSequence
    #sg = SeedSequence(123)
    rng = Generator(MT19937(semilla))
    c_len = len(code)
    

    #N_bits de rafaga <- array de errores
    rafaga = rng.integers(low = 0, high = 1, size = nErrores - 1, endpoint = True)
    
    #Posiciones del subarray

    if (c_len - nErrores > 0):
        pos = rng.integers(low = 0, high = c_len - nErrores, size = 1)
        pos = pos[0]
    else:
        pos = 0
    
    if code[pos]:
        code[pos] = 0
    else:
        code[pos] = 1
   
    #Rafaga y lugares en la rafaga
    for i in range (nErrores - 1): #Cantidad de errores
        code[pos + 1 + i] = rafaga[i]   #Pos-> posicion de los errores
    c_ret = code
    #print(c_ret)
    return c_ret

#Implementado
def validador(crc_ret:int):
    c_len = len(crc_ret)
    c_val = True
    for i in range (c_len):
        if crc_ret[i] != 0:
            c_val = False

    return c_val

#Tests

semilla = 235
divisor = '1101'
c = cyclic_redundancy_check('test.txt', '1'+divisor, 4)
# print("Codigo+CRC: ", c)

''' Test de generadorErrores
for i in range(500):
    a = bitarray('0000000000')
    b = generadorErrores(a.copy(), 5)
    print(a, b)
'''

''''''
d_1 = 0
d_2 = 0
d_3 = 0
o_1 = 0
o_2 = 0
o_3 = 0

print('\nCaso n = 4 (r <= n)')
for i in range(100):
    r_1 = generadorErrores(c.copy(), 4, semilla)
    semilla += 1
    dec = decoder('1'+ divisor , r_1 , 4)
    #print(dec)
    if validador(dec) == False:
        d_1 += 1
    else:
        o_1 +=1

print("Numero de detecciones:",d_1)
print("Numero de omisiones:",o_1)
print("Probabilidad:", d_1 / 100)


print('\nCaso n = 5 (n = r + 1)')
for i in range(100):
    r_1 = generadorErrores(c,5, semilla)
    semilla += 1
    dec = decoder('1'+divisor, r_1, 4)
    if validador(dec) == False:
        d_2 += 1
    else:
        o_2 +=1

print("Numero de detecciones:",d_2)
print("Numero de omisiones:",o_2)
print("Probabilidad:", d_2 / 100)

print('\nCaso n = 5 (n > r + 1)')
for i in range(100):
    r_1 = generadorErrores(c,6,  semilla)
    semilla += 1
    dec = decoder('1'+divisor, r_1, 4)
    if validador(dec) == False:
        d_3 += 1
    else:
        o_3 +=1

print("Numero de detecciones:",d_3)
print("Numero de omisiones:",o_3)
print("Probabilidad:", d_3 / 100)
