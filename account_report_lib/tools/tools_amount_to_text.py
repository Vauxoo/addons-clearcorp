#!/usr/bin/python                   
# -*- coding: utf-8 -*-

UNIDADES = (
    '',     
    'UN ',  
    'DOS ', 
    'TRES ',
    'CUATRO ',
    'CINCO ', 
    'SEIS ',  
    'SIETE ', 
    'OCHO ',  
    'NUEVE ', 
    'DIEZ ',  
    'ONCE ',  
    'DOCE ',  
    'TRECE ', 
    'CATORCE ',
    'QUINCE ', 
    'DIECISEIS ',
    'DIECISIETE ',
    'DIECIOCHO ', 
    'DIECINUEVE ',
    'VEINTE '     
)                 
DECENAS = (       
    'VENTI',      
    'TREINTA ',   
    'CUARENTA ',  
    'CINCUENTA ', 
    'SESENTA ',   
    'SETENTA ',   
    'OCHENTA ',   
    'NOVENTA ',   
    'CIEN '       
)                 
CENTENAS = (      
    'CIENTO ',    
    'DOSCIENTOS ',
    'TRESCIENTOS ',
    'CUATROCIENTOS ',
    'QUINIENTOS ',   
    'SEISCIENTOS ',  
    'SETECIENTOS ',  
    'OCHOCIENTOS ',  
    'NOVECIENTOS '   
)                    
                     
def number_to_text_es(number_in,currency,join_dec=' Y ',separator=',',decimal_point='.'):
                              
    converted = ''                              
    if currency == False:
        currency = ''
        
    if currency == None:
        currency = ''

    if type(number_in) != 'str':
      number = str(number_in)   
    else:                       
      number = number_in        
     
    number_str=number
    #if we are using the coma as separator we need to remove them from the string
    try:
      number_str = number_str.replace(separator,'')
    except ValueError:
      print 'The separator used for the thousands its not supported'
    
    #debug(number_str)                                      
                                                           
    try:                                                   
      number_int, number_dec = number_str.split(decimal_point)       
    except ValueError:                                     
      number_int = number_str                              
      number_dec = ""                                      

    number_str = number_int.zfill(9)
    millones = number_str[:3]       
    miles = number_str[3:6]         
    cientos = number_str[6:]        

    if(millones):
        if(millones == '001'):
            converted += 'UN MILLON '
        elif(int(millones) > 0):     
            converted += '%sMILLONES ' % __convertNumber(millones)
                                                                  
    if(miles):                                                    
        if(miles == '001'):                                       
            converted += 'MIL '                                   
        elif(int(miles) > 0):                                     
            converted += '%sMIL ' % __convertNumber(miles)        
    if(cientos):                                                  
        if(cientos == '001'):                                     
            converted += 'UN '                                    
        elif(int(cientos) > 0):                                   
            converted += '%s ' % __convertNumber(cientos)         

    if number_dec == "":
      number_dec = "00" 
    if (len(number_dec) < 2 ):
      number_dec+='0'         

    has_decimal = float(number_dec) != 0 and join_dec + number_dec + "/100" or ' EXACTOS'
    converted += currency +  has_decimal
    

    return converted
                    
def __convertNumber(n):
    output = ''

    if(n == '100'):
        output = "CIEN "
    elif(n[0] != '0'):
        output = CENTENAS[int(n[0])-1]

    k = int(n[1:])
    if(k <= 20):
        output += UNIDADES[k]
    else:
        if((k > 30) & (n[2] != '0')):
            output += '%sY %s' % (DECENAS[int(n[1])-2], UNIDADES[int(n[2])])
        else:
            output += '%s%s' % (DECENAS[int(n[1])-2], UNIDADES[int(n[2])])

    return output
