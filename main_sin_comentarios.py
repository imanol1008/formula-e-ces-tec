from machine import Pin, PWM, ADC
import time, sys, select

DATA, CLK = Pin(2, Pin.OUT), Pin(3, Pin.OUT)
IN1, IN2, IN3, IN4 = [Pin(n, Pin.OUT) for n in (10, 11, 13, 14)]
ENA, ENB = PWM(Pin(12)), PWM(Pin(15))
ENA.freq(1000)
ENB.freq(1000)
SENSOR = ADC(Pin(26))

VELOCIDAD = 70
FUERZA_GIRO = 90
UMBRAL_OSCURO = 30
INVERTIR_SENSOR = False
TIEMPO_CIRCULO = 4000
TIEMPO_ZIGZAG = 700
TRAMOS_ZIGZAG = 6
PARPADEO = 400

PRINCIPALES = 0b00001111
DIR_IZQ     = 0b01010000
DIR_DER     = 0b10100000

luces = False
direccional = 0
oscuro = False


def enviar(byte):
    for i in range(7, -1, -1):
        DATA.value(1 - (byte >> i & 1))
        CLK.value(1)
        CLK.value(0)


def luz():
    p = SENSOR.read_u16() * 100 // 65535
    return 100 - p if INVERTIR_SENSOR else p


def actualizar_luces():
    global oscuro
    p = luz()
    if p < UMBRAL_OSCURO:
        oscuro = True
    elif p > UMBRAL_OSCURO + 10:
        oscuro = False
    byte = PRINCIPALES if (luces or oscuro) else 0
    if time.ticks_ms() // PARPADEO % 2:
        byte |= direccional
    enviar(byte)


def motor(a, b, en, p):
    a.value(int(p > 0))
    b.value(int(p < 0))
    en.duty_u16(abs(p) * 65535 // 100)


def mover(p):
    motor(IN1, IN2, ENA, p)


def girar(p):
    global direccional
    motor(IN4, IN3, ENB, p)
    direccional = DIR_DER if p > 0 else DIR_IZQ if p < 0 else 0


def parar():
    mover(0)
    girar(0)


def esperar(ms):
    fin = time.ticks_add(time.ticks_ms(), ms)
    while time.ticks_diff(fin, time.ticks_ms()) > 0:
        actualizar_luces()
        time.sleep_ms(20)


def rutina(pasos):
    mover(VELOCIDAD)
    for giro, ms in pasos:
        girar(giro)
        esperar(ms)
    parar()


AYUDA = """
---------------- COMANDOS ----------------
 ADELANTE   ATRAS   IZQUIERDA   DERECHA
 RECTO      PARAR   VELOCIDAD 0-100
 LUCES ON | LUCES OFF   (con oscuridad se encienden solas)
 DIR IZQ | DIR DER | DIR EMERGENCIA | DIR OFF
 CIRCULO    INFINITO    ZIGZAG
 SENSOR (muestra el % de luz)    AYUDA
------------------------------------------
"""


def ejecutar(texto):
    global VELOCIDAD, luces, direccional
    p = texto.strip().upper().split()
    if not p:
        return
    orden = p[0]
    valor = p[1] if len(p) > 1 else ""
    F, C, Z = FUERZA_GIRO, TIEMPO_CIRCULO, TIEMPO_ZIGZAG

    if orden == "ADELANTE":   mover(VELOCIDAD)
    elif orden == "ATRAS":    mover(-VELOCIDAD)
    elif orden == "IZQUIERDA": girar(-F)
    elif orden == "DERECHA":  girar(F)
    elif orden == "RECTO":    girar(0)
    elif orden == "PARAR":    parar()
    elif orden == "VELOCIDAD": VELOCIDAD = int(valor)
    elif orden == "LUCES" and valor in ("ON", "OFF"):
        luces = valor == "ON"
    elif orden == "DIR" and valor in ("IZQ", "DER", "EMERGENCIA", "OFF"):
        direccional = {"IZQ": DIR_IZQ, "DER": DIR_DER,
                       "EMERGENCIA": DIR_IZQ | DIR_DER, "OFF": 0}[valor]
    elif orden == "CIRCULO":  rutina([(-F, C)])
    elif orden == "INFINITO": rutina([(-F, C), (F, C)])
    elif orden == "ZIGZAG":   rutina([(F if i % 2 else -F, Z) for i in range(TRAMOS_ZIGZAG)])
    elif orden == "SENSOR":   print("Luz:", luz(), "%  Oscuro:", oscuro)
    elif orden == "AYUDA":    print(AYUDA)
    else:
        print("Comando no reconocido. Escriba AYUDA")
        return
    print("OK:", " ".join(p))


def programa_principal():
    consola = select.poll()
    consola.register(sys.stdin, select.POLLIN)
    texto = ""
    parar()
    print(AYUDA)
    while True:
        actualizar_luces()
        while consola.poll(0):
            letra = sys.stdin.read(1)
            if letra in "\r\n":
                try:
                    ejecutar(texto)
                except ValueError:
                    print("Numero no valido. Ejemplo: VELOCIDAD 60")
                texto = ""
            else:
                texto += letra
        time.sleep_ms(20)


try:
    programa_principal()
finally:
    parar()
    enviar(0)
