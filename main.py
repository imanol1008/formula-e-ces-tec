#Carrito Formula E CES TEC - Parte 2
#Código de la Raspberry Pi Pico W ( se corre en Thonny con MicroPython )
#Recibe los comandos que manda la interfaz por Wi-Fi y tambien desde la consola de Thonny.

from machine import Pin, PWM, ADC
import time
import sys
import select
import network
import socket


#Pines de la parte 1
DATA = Pin(2, Pin.OUT)      #Registro de corrimiento 74LS164
CLK = Pin(3, Pin.OUT)
IN1 = Pin(10, Pin.OUT)      #Motor trasero ( L298N )
IN2 = Pin(11, Pin.OUT)
ENA = PWM(Pin(12))
IN3 = Pin(13, Pin.OUT)      #Motor de direccion ( L298N )
IN4 = Pin(14, Pin.OUT)
ENB = PWM(Pin(15))
ENA.freq(200)
ENB.freq(200)
SENSOR = ADC(Pin(26))       #Fotorresistencia
LED_PLACA = Pin("LED", Pin.OUT)

#Pines de la parte 2 ( decrementador )

#Entradas del circuito ( salen de la Pico )
ENTRADA_A = Pin(4, Pin.OUT)
ENTRADA_B = Pin(5, Pin.OUT)
ENTRADA_C = Pin(6, Pin.OUT)

#Salidas del circuito ( entran a la Pico pasando por el divisor de tensión )
SALIDA_X = Pin(7, Pin.IN)
SALIDA_Y = Pin(8, Pin.IN)
SALIDA_Z = Pin(9, Pin.IN)

#Posición de cada LED en la lista que se manda al 74LS164:
#0-3 son las luces principales y 4-7 las direccionales ( izq, der, izq, der ).
#Aquí se escoge en que LEDs frontales se ven X, Y y Z. Cambiar si en el carro quedan en otro orden.
LEDS_RESULTADO = [4, 0, 1]


RED_NOMBRE = "iPhone de Ale"
RED_CLAVE = "Alexa310805"

velocidad = 70
VELOCIDAD_MINIMA = 65
IMPULSO_MS = 200
FUERZA_GIRO = 90
UMBRAL_OSCURO = 30
UMBRAL_CLARO = 40
TIEMPO_CIRCULO = 4000
TIEMPO_ZIGZAG = 700
TRAMOS_ZIGZAG = 6
PARPADEO = 400


modo = "ESTANDAR"           #ESTANDAR o DECREMENTO
resultado = [0, 0, 0]       #Último resultado del decrementador ( X, Y, Z )
modo_luces = "AUTO"
direccional = "OFF"
oscuro = False
sentido = 0
ultimo_envio = None


#Luces
def enviar_leds(leds):
    #Manda los 8 bits al registro de corrimiento ( solo si cambiaron )
    global ultimo_envio
    if leds == ultimo_envio:
        return
    ultimo_envio = leds
    for encendido in reversed(leds):
        DATA.value(0 if encendido else 1)
        CLK.value(1)
        CLK.value(0)


def luz():
    #Porcentaje de luz que lee la fotorresistencia
    return SENSOR.read_u16() * 100 // 65535


def actualizar_luces():
    global oscuro

    #En modo decremento los LEDs frontales muestran el resultado X, Y, Z
    if modo == "DECREMENTO":
        leds = [False] * 8
        for i in range(3):
            leds[LEDS_RESULTADO[i]] = resultado[i] == 1
        enviar_leds(leds)
        return

    nivel = luz()
    if nivel < UMBRAL_OSCURO:
        oscuro = True
    elif nivel > UMBRAL_CLARO:
        oscuro = False

    principales = modo_luces == "ON" or (modo_luces == "AUTO" and oscuro)
    prendida = (time.ticks_ms() // PARPADEO) % 2 == 0
    izq = prendida and direccional in ("IZQ", "EMERGENCIA")
    der = prendida and direccional in ("DER", "EMERGENCIA")

    enviar_leds([principales] * 4 + [izq, der, izq, der])


#Motores
def motor_trasero(potencia):
    IN1.value(1 if potencia < 0 else 0)
    IN2.value(1 if potencia > 0 else 0)
    if potencia == 0:
        real = 0
    else:
        real = VELOCIDAD_MINIMA + (100 - VELOCIDAD_MINIMA) * (abs(potencia) - 1) // 99
    ENA.duty_u16(real * 65535 // 100)


def girar(lado):
    #Lado: -1 izquierda, 0 recto, 1 derecha
    global direccional
    IN3.value(1 if lado < 0 else 0)
    IN4.value(1 if lado > 0 else 0)
    ENB.duty_u16(abs(lado) * FUERZA_GIRO * 65535 // 100)
    direccional = ("IZQ", "OFF", "DER")[lado + 1]


def andar(nuevo_sentido):
    #Nuevo_sentido: 1 adelante, -1 atras, 0 detenido
    global sentido
    if nuevo_sentido != 0 and nuevo_sentido != sentido and velocidad > 0:
        motor_trasero(nuevo_sentido * 100)   # impulso para que arranque
        esperar(IMPULSO_MS)
    sentido = nuevo_sentido
    motor_trasero(sentido * velocidad)


def parar():
    andar(0)
    girar(0)


def esperar(ms):
    #Espera sin dejar de actualizar las luces
    inicio = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), inicio) < ms:
        actualizar_luces()
        time.sleep_ms(20)


#Patrones
def circulo():
    andar(1)
    girar(-1)
    esperar(TIEMPO_CIRCULO)
    parar()


def infinito():
    andar(1)
    girar(-1)
    esperar(TIEMPO_CIRCULO)
    girar(1)
    esperar(TIEMPO_CIRCULO)
    parar()


def zigzag():
    andar(1)
    for tramo in range(TRAMOS_ZIGZAG):
        girar(-1 if tramo % 2 == 0 else 1)
        esperar(TIEMPO_ZIGZAG)
    parar()


#Decrementador ( Parte 2 )
    
def decrementar(numero):
    
    #Pone el número ( 0 a 7 ) en A, B, C y lee lo que devuelve el circuito en X, Y, Z
    global resultado
    ENTRADA_A.value(numero // 4 % 2)
    ENTRADA_B.value(numero // 2 % 2)
    ENTRADA_C.value(numero % 2)
    time.sleep_ms(10)   #Tiempo para que las compuertas respondan
    resultado = [SALIDA_X.value(), SALIDA_Y.value(), SALIDA_Z.value()]
    salida = resultado[0] * 4 + resultado[1] * 2 + resultado[2]

    entrada_bits = str(numero // 4 % 2) + str(numero // 2 % 2) + str(numero % 2)
    salida_bits = str(resultado[0]) + str(resultado[1]) + str(resultado[2])
    return "Entrada " + entrada_bits + " (" + str(numero) + ") -> Salida " + salida_bits + " (" + str(salida) + ")"


def probar():
    
    #Prueba las 8 combinaciones de A, B, C y compara con el resultado esperado
    texto = "A B C | X Y Z leido | X Y Z esperado\n"
    correctas = 0
    for n in range(8):
        decrementar(n)
        esperado = (n - 5) % 8
        leido = resultado[0] * 4 + resultado[1] * 2 + resultado[2]
        if leido == esperado:
            correctas += 1
            marca = "OK"
        else:
            marca = "ERROR"
        texto += str(n // 4 % 2) + " " + str(n // 2 % 2) + " " + str(n % 2) + " |    "
        texto += str(resultado[0]) + " " + str(resultado[1]) + " " + str(resultado[2]) + "    |     "
        texto += str(esperado // 4 % 2) + " " + str(esperado // 2 % 2) + " " + str(esperado % 2)
        texto += "      " + marca + "\n"
    texto += "Resultado: " + str(correctas) + "/8 correctas"
    return texto


#Comandos
AYUDA = """MODO ESTANDAR/DECREMENTO
ADELANTE ATRAS IZQUIERDA DERECHA RECTO PARAR VELOCIDAD 0-100
LUCES ON/OFF/AUTO  DIR IZQ/DER/EMERGENCIA/OFF
CIRCULO INFINITO ZIGZAG SENSOR
DEC 0-7  PRUEBA (solo en modo decremento)  AYUDA"""


def ejecutar(texto):
    global velocidad, modo_luces, direccional, modo
    partes = texto.upper().split()
    if not partes:
        return "Carrito listo"
    orden = partes[0]
    valor = partes[1] if len(partes) > 1 else ""

    if orden == "MODO" and valor in ("ESTANDAR", "DECREMENTO"):
        parar()
        modo = valor
    elif orden == "DEC" and valor.isdigit() and int(valor) <= 7:
        if modo != "DECREMENTO":
            return "Primero cambie a MODO DECREMENTO"
        return decrementar(int(valor))
    elif orden == "PRUEBA":
        if modo != "DECREMENTO":
            return "Primero cambie a MODO DECREMENTO"
        return probar()
    elif orden == "ADELANTE":
        andar(1)
    elif orden == "ATRAS":
        andar(-1)
    elif orden == "IZQUIERDA":
        girar(-1)
    elif orden == "DERECHA":
        girar(1)
    elif orden == "RECTO":
        girar(0)
    elif orden == "PARAR":
        parar()
    elif orden == "VELOCIDAD" and valor.isdigit():
        velocidad = min(100, int(valor))
        motor_trasero(sentido * velocidad)
    elif orden == "LUCES" and valor in ("ON", "OFF", "AUTO"):
        modo_luces = valor
    elif orden == "DIR" and valor in ("IZQ", "DER", "EMERGENCIA", "OFF"):
        direccional = valor
    elif orden == "CIRCULO":
        circulo()
    elif orden == "INFINITO":
        infinito()
    elif orden == "ZIGZAG":
        zigzag()
    elif orden == "SENSOR":
        return "Luz: " + str(luz()) + " %"
    elif orden == "AYUDA":
        return AYUDA
    else:
        return "Comando no reconocido: " + texto
    return "OK: " + " ".join(partes)


#Wi-Fi
red = network.WLAN(network.STA_IF)
red.active(True)
red.connect(RED_NOMBRE, RED_CLAVE)
servidor = None
ultimo_intento = time.ticks_ms()


def revisar_wifi():
    
    #Revisa la conexion y atiende a la interfaz si mando un comando
    global servidor, ultimo_intento
    ahora = time.ticks_ms()

    if not red.isconnected():
        LED_PLACA.value((ahora // 500) % 2)     #LED parpadea = Sin Wi-Fi
        if servidor is not None:
            servidor.close()
            servidor = None
        if time.ticks_diff(ahora, ultimo_intento) > 20000:
            ultimo_intento = ahora
            red.disconnect()
            red.connect(RED_NOMBRE, RED_CLAVE)
        return

    LED_PLACA.value(1)                          #LED fijo = Conectado
    if servidor is None:
        servidor = socket.socket()
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind(("0.0.0.0", 80))
        servidor.listen(2)
        servidor.setblocking(False)
        print("Conectado a", RED_NOMBRE, "- direccion de la Pico:", red.ifconfig()[0])

    try:
        cliente, _ = servidor.accept()
    except OSError:
        return
    try:
        cliente.settimeout(3)
        ruta = cliente.recv(1024).decode().split(" ")[1]
        comando = ruta.split("?c=")[1] if "?c=" in ruta else ""
        comando = comando.replace("%20", " ").replace("+", " ")
        respuesta = ejecutar(comando)
        cliente.sendall("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n" + respuesta)
    finally:
        cliente.close()


#Programa principal
consola = select.poll()
consola.register(sys.stdin, select.POLLIN)
texto = ""

parar()
print(AYUDA)
print("Conectando a", RED_NOMBRE, "...")

try:
    while True:
        try:
            actualizar_luces()
            revisar_wifi()
            #Comandos escritos en la consola de Thonny ( para pruebas )
            if consola.poll(0):
                letra = sys.stdin.read(1)
                if letra in ("\r", "\n"):
                    if texto.strip():
                        print(ejecutar(texto))
                    texto = ""
                else:
                    texto += letra
        except Exception as error:
            parar()
            print("ERROR:", error)
            texto = ""
            if servidor is not None:
                servidor.close()
                servidor = None
        time.sleep_ms(20)
finally:
    parar()
    enviar_leds([False] * 8)
