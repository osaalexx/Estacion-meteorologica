# Estacion-meteorologica

El objetivo de este proyecto es el de crear una estación de lectura de parámetros atmosféricos, el cual funcionará de manera automática, remota y necesitará de una interacción mínima con el usuario.
Para llevar todo esto a cabo, se utilizan un ordenador de placa reducida (una Raspberry Pi 3b+), un sensor digital de temperatura y humedad DHT11 y una plataforma IoT de almacenamiento en la nube (ThingSpeak en este caso). En cuanto a la codificación, para la obtención y el envío de datos a ThingSpeak, se utiliza el lenguaje de programación Python. La página web para la visualización está codificada en HTML y D3.js.

Para poder usar estos códigos en canales propios de ThingSpeak, primero habrá que actualizar el User API Key en el archivo de Python thingSpeak_datalogger.py. Una vez creados los canales en la cuenta de ThingSpeak, habrá que actualizar los channel ID en los siguientes archivos: CondClimaticaHogar.html y analisis_datos.m.

Se puede encontrar una documentación más extensa en una serie de entradas en el siguiente blog: https://laingenieriaencasa.blogspot.com/
