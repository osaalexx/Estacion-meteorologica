# Para poder introducir tildes y caracteres especiales
# encoding=utf8

"""
@Autor: Alexander Osa
@Descripcion:
@   Este programa crea un canal en ThingSpeak, lee los datos de temperatura y humedad del sensor DHT22 y los sube al
@   canal creado.
"""

########################################################################################################################
#                                         Importar las librerias                                                       #
########################################################################################################################
import urllib
import httplib
import json
import Adafruit_DHT as DHT
import time

########################################################################################################################
#                                         Definir constantes                                                           #
########################################################################################################################
server = 'api.thingspeak.com' # Servidor al cual se suben los datos
USER_API_KEY = 'FZYAXN2QNTUGX3VN' # En el perfil de ThingSpeak -> ThingSpeak settings -> User API Key
sensor_args = { '11' : DHT.DHT11,
                '22' : DHT.DHT22,
                '2302' : DHT.AM2302 } # Los distintos sensores en la libreria
sensor = sensor_args['11'] # El sensor especifico que se usa
pin = 4 # El pin al que se conecta el sensor
intervalo = 10 # Intervalo de tiempo entre los que se suben los datos

########################################################################################################################
#                                         Funciones                                                                    #
########################################################################################################################
def create_channel(nombre_canal):
    # Crear el canal para poder introducir nuevos datos
    # https://es.mathworks.com/help/thingspeak/createchannel.html
    print("Creando canal '" + nombre_canal + "'")
    method = 'POST'
    relative_uri = "/channels.json"
    headers = {'Host': server,
               'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'api_key': USER_API_KEY,
               'description': 'Informacion de temperatura y humedad obtenidas desde la estacion meteorologica',
               'field1': 'Temperatura',
               'field2': 'Humedad',
               'name': nombre_canal,
               'public_flag': 'true'}
    # Codificar los datos a enviar en formato form ('field1'=5&...)
    payload_encoded = urllib.urlencode(payload)
    headers['Content-Length'] = len(payload_encoded)

    # Enviar la peticion http
    connTCP.request(method, relative_uri, body=payload_encoded, headers=headers)

    # Guardar la respuesta recivida en una variable
    respuesta = connTCP.getresponse()
    # En caso de asi desearlo, se puede mostrar el estado en la respuesta (200 si todo ha ido bien)
    #status = respuesta.status
    
    # Leer la respuesta y guardarla en una variable (hay que hacerlo siempre que se haga una peticion)
    contenido = respuesta.read()
    contenido_json = json.loads(contenido)  # Se copia contenido en formato json a un diccionario
    
    return contenido_json

def subir_datos(canal, clave_API, dato1, dato2):
    # Crear la peticion http que sube datos al canal de ThingSpeak
    # https://es.mathworks.com/help/thingspeak/writedata.html
    print("Subiendo datos a '" + canal + "'...")
    method = "POST"
    relative_uri = "/update.json"
    headers = {'Host': server,
               'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'api_key': clave_API,
               'field1': dato1,
               'field2': dato2}
    # Codificar los datos a enviar en formato form ('field1'=5&...)
    payload_encoded = urllib.urlencode(payload)
    headers['Content-Length'] = len(payload_encoded)

    # Enviar la peticion http
    connTCP.request(method, relative_uri, body=payload_encoded, headers=headers)

    # Guardar la respuesta recivida en una variable
    respuesta = connTCP.getresponse()
    # En caso de asi desearlo, se puede mostrar el estado en la respuesta (200 si todo ha ido bien)
    #status = respuesta.status
    
    # Leer la respuesta y guardarla en una variable (hay que hacerlo siempre que se haga una peticion)
    respuesta.read()

    return

########################################################################################################################
#                                         Establecer conexion TCP                                                      #
########################################################################################################################
# Con es la variable o el objeto que hace referencia a la conexion TCP
connTCP = httplib.HTTPSConnection(server)
print("Estableciendo conexion TCP...")
connTCP.connect() # Establecer conexion
print("Conexion TCP establecida\n")

########################################################################################################################
#                                         Crear canales                                                                #
########################################################################################################################
contenido_json_1 = create_channel('Estacion meteorologica 1')
# Se consiguen las variables necesarias de la respuesta de la funcion
CHANNEL_ID_1 = contenido_json_1['id']
WRITE_API_KEY_1 = contenido_json_1['api_keys'][0]['api_key']

contenido_json_2 = create_channel('Estacion meteorologica 2')
# Se consiguen las variables necesarias de la respuesta de la funcion
CHANNEL_ID_2 = contenido_json_2['id']
WRITE_API_KEY_2 = contenido_json_2['api_keys'][0]['api_key']

########################################################################################################################
#                                         Inicializacion de variables                                                  #
########################################################################################################################
hum = 0
temp = 0
humDefault = hum
tempDefault = temp
next_time = 0

########################################################################################################################
#                                         Programa principal                                                           #
########################################################################################################################

try:
    while (True):
        contador = 0
        
        # Leer los datos del sensor
        hum, temp = DHT.read(sensor, pin)
        
        # El codigo se queda en bucle en el while hasta que haya pasado el margen de tiempo especificado por el usuario
        while time.time() < next_time:
            # Si no se han cogido medidas o estas son erroneas, se vuelven a tomar
            if ((hum is None and temp is None) or (hum > 100)) and contador < 3:
                time.sleep(2)
                hum, temp = DHT.read(sensor, pin)
                contador = contador + 1
            else:
                pass
            
            # Si no hay datos o siguen siendo erroneos tras 3 intentos, se muestra un mensaje de error y
            # se resube el ultimo valor
            if ((hum is None and temp is None) or (hum > 100)) and contador == 3:
                hum = humDefault
                temp = tempDefault
                print("Fallo de lectura. Se reenviaran los ultimos datos.")

        # Los datos se suben a ThingSpeak
        print("\nTemperatura: " + str(temp) + " C\tHumedad: " + str(hum) + "%")
        subir_datos('Estacion meteorologica 1', WRITE_API_KEY_1, temp, hum)
        
        humDefault = hum
        tempDefault = temp

        next_time = time.time() + intervalo - 0.1 # Se resta 0,1 porque se necesitara un tiempo para subir los datos
        contador = 0
        
        # Leer los datos del sensor
        hum, temp = DHT.read(sensor, pin)
        
        # El codigo se queda en bucle en el while hasta que haya pasado el margen de tiempo especificado por el usuario
        while time.time() < next_time:
            # Si no se han cogido medidas o estas son erroneas, se vuelven a tomar
            if ((hum is None and temp is None) or (hum > 100)) and contador < 3:
                time.sleep(2)
                hum, temp = DHT.read(sensor, pin)
                contador = contador + 1
            else:
                pass
            
            # Si no hay datos o siguen siendo erroneos tras 3 intentos, se muestra un mensaje de error y
            # se resube el ultimo valor
            if hum is None and temp is None and contador == 3:
                hum = humDefault
                temp = tempDefault
                print("Fallo de lectura. Se reenviaran los ultimos datos.")

        # Los datos se suben a ThingSpeak
        print("\nTemperatura: " + str(temp) + " C\tHumedad: " + str(hum) + "%")
        subir_datos('Estacion meteorologica 2', WRITE_API_KEY_2, temp, hum)
        
        humDefault = hum
        tempDefault = temp
        
        next_time = time.time() + intervalo - 0.1 # Se resta 0,1 porque se necesitara un tiempo para subir los datos
            
except KeyboardInterrupt:
    # Cuando se interrumpe el programa con el teclado (ctrl + C), se interrumpe el programa principal y se cierra la
    # conexion TCP establecida con el servidor, finalizando el programa
    connTCP.close()
    print("\nSe ha pulsado Ctrl+C. Saliendo del programa...\n")