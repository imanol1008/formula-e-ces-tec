#Carrito Formula E CES TEC - Parte 2
#Programa de pruebas manuales del decrementador 
#Se escriben los 3 bits de entrada con el teclado, la Pico los pone en A, B y C; lee X, Y, Z del circuito y los muestra en los LEDs del carro.

import urllib.request
import urllib.parse

IP_DE_LA_PICO = "172.20.10.2"

conexion = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def enviar(ip, comando, espera):
    url = "http://" + ip + "/?c=" + urllib.parse.quote(comando)
    return conexion.open(url, timeout=espera).read().decode()


#Buscar el carrito en la red del iPhone
ip = None
for candidata in [IP_DE_LA_PICO] + ["172.20.10." + str(n) for n in range(2, 11)]:
    try:
        if "Carrito" in enviar(candidata, "", 2):
            ip = candidata
            break
    except Exception:
        pass

if ip is None:
    print("No se encontró el carrito. Revise que el LED de la Pico esté fijo")
    print("y que la computadora esté conectada a la red del iPhone.")
else:
    print("Carrito encontrado en", ip)
    enviar(ip, "MODO DECREMENTO", 20)
    print("Escriba los 3 bits de entrada A B C (por ejemplo 101). Escriba SALIR para terminar.")

    while True:
        bits = input("Bits A B C: ").strip().replace(" ", "")
        if bits.upper() == "SALIR":
            break
        if len(bits) != 3 or bits.strip("01") != "":
            print("Escriba exactamente 3 bits, solo ceros y unos (por ejemplo 011).")
            continue

        numero = int(bits[0]) * 4 + int(bits[1]) * 2 + int(bits[2])
        esperado = (numero - 5) % 8
        esperado_bits = str(esperado // 4 % 2) + str(esperado // 2 % 2) + str(esperado % 2)
        try:
            print(enviar(ip, "DEC " + str(numero), 20))
            print("Esperado: " + esperado_bits + " (" + str(esperado) + ")  -> revise los LEDs del carro")
        except Exception as error:
            print("No se pudo enviar:", error)

    enviar(ip, "MODO ESTANDAR", 20)
    print("Prueba terminada")
