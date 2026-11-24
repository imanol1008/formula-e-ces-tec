#Carrito Formula E CES TEC - Parte 2
#Interfaz gráfica

#Manda los comandos a la Pico por Wi-Fi. La compu debe estar conectada al hotspot del iPhone.

import tkinter as tk
import os
import urllib.request
import urllib.parse

IP_DE_LA_PICO = "172.20.10.2"

#Colores del diseño
FONDO = "#C6EEF8"      
LETRA = "#0D3B8C"
BOTONES = "#0D3B8C"    

conexion = urllib.request.build_opener(urllib.request.ProxyHandler({}))
ip = None


#Comunicacion con la Pico
def pedir(direccion, comando, espera):
    url = "http://" + direccion + "/?c=" + urllib.parse.quote(comando)
    return conexion.open(url, timeout=espera).read().decode()


def buscar_carrito():
    #Prueba la IP guardada y si no, las demas IPs del hotspot
    global ip
    estado.config(text="Buscando el carrito...")
    ventana.update()
    for candidata in [IP_DE_LA_PICO] + ["172.20.10." + str(n) for n in range(2, 11)]:
        try:
            if "Carrito" in pedir(candidata, "", 2):
                ip = candidata
                estado.config(text="Carrito conectado en " + ip)
                return
        except Exception:
            pass
    estado.config(text="No se encontró el carrito. Revise el LED de la Pico y el Wi-Fi.")


def enviar(comando):
    #Manda un comando y muestra la respuesta abajo en la ventana
    if ip is None:
        estado.config(text="El carrito no está conectado (presione Reconectar)")
        return ""
    estado.config(text="Enviando: " + comando)
    ventana.update()
    try:
        respuesta = pedir(ip, comando, 20)
    except Exception as error:
        respuesta = "No se pudo enviar: " + str(error)
    estado.config(text=respuesta)
    return respuesta


#Cambio de modo
def modo_estandar():
    enviar("MODO ESTANDAR")
    marco_decremento.pack_forget()
    marco_estandar.pack(pady=10)


def modo_decremento():
    enviar("MODO DECREMENTO")
    marco_estandar.pack_forget()
    marco_decremento.pack(pady=10)


#Modo decremento
def numero_elegido():
    return a.get() * 4 + b.get() * 2 + c.get()


def mostrar_numero():
    numero_texto.config(text="Número de entrada: " + str(numero_elegido()))


def decrementar():
    numero = numero_elegido()
    respuesta = enviar("DEC " + str(numero))
    esperado = (numero - 5) % 8
    resultado_texto.config(text=respuesta + "\nValor esperado: " + str(esperado))


def probar_todo():
    #Le pide a la Pico que pruebe las 8 combinaciones y muestra la tabla
    respuesta = enviar("PRUEBA")
    resultado_texto.config(text=respuesta)
    estado.config(text="Prueba terminada")


#Ventana
ventana = tk.Tk()
ventana.title("Carrito Fórmula E CES TEC")
ventana.geometry("560x700")
ventana.configure(bg=FONDO)

#Colores para todo lo que se crea despues
ventana.option_add("*Background", FONDO)
ventana.option_add("*Foreground", LETRA)
ventana.option_add("*Button.Background", BOTONES)
ventana.option_add("*Button.activeBackground", BOTONES)
ventana.option_add("*Button.activeForeground", LETRA)
ventana.option_add("*Checkbutton.selectColor", BOTONES)
ventana.option_add("*Checkbutton.activeBackground", FONDO)
ventana.option_add("*Checkbutton.activeForeground", LETRA)
ventana.option_add("*Scale.troughColor", BOTONES)
ventana.option_add("*Scale.highlightThickness", 0)

#Logo centrado
logo = tk.PhotoImage(file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "formula_TEC.png")).subsample(4)
tk.Label(ventana, image=logo).pack(pady=8)

tk.Label(ventana, text="Carrito Fórmula E CES TEC", font=("Arial", 16, "bold")).pack(pady=5)

marco_modos = tk.Frame(ventana)
marco_modos.pack()
tk.Button(marco_modos, text="Modo estándar", width=16, command=modo_estandar).grid(row=0, column=0, padx=5)
tk.Button(marco_modos, text="Modo decremento", width=16, command=modo_decremento).grid(row=0, column=1, padx=5)


def boton(marco, texto, comando, fila, columna):
    #Crea un boton que manda un comando a la Pico
    tk.Button(marco, text=texto, width=11, command=lambda: enviar(comando)).grid(row=fila, column=columna, padx=3, pady=3)


#Marco del modo estandar ( parte 1 del proyecto )
marco_estandar = tk.Frame(ventana)

tk.Label(marco_estandar, text="Movimiento:").grid(row=0, column=0, sticky="w")
boton(marco_estandar, "Adelante", "ADELANTE", 0, 1)
boton(marco_estandar, "Atrás", "ATRAS", 0, 2)
boton(marco_estandar, "Parar", "PARAR", 0, 3)

tk.Label(marco_estandar, text="Dirección:").grid(row=1, column=0, sticky="w")
boton(marco_estandar, "Izquierda", "IZQUIERDA", 1, 1)
boton(marco_estandar, "Recto", "RECTO", 1, 2)
boton(marco_estandar, "Derecha", "DERECHA", 1, 3)

tk.Label(marco_estandar, text="Velocidad:").grid(row=2, column=0, sticky="w")
velocidad = tk.Scale(marco_estandar, from_=0, to=100, orient="horizontal")
velocidad.set(70)
velocidad.grid(row=2, column=1, columnspan=2, sticky="we")
tk.Button(marco_estandar, text="Aplicar", width=11,
          command=lambda: enviar("VELOCIDAD " + str(velocidad.get()))).grid(row=2, column=3)

tk.Label(marco_estandar, text="Luces:").grid(row=3, column=0, sticky="w")
boton(marco_estandar, "Encender", "LUCES ON", 3, 1)
boton(marco_estandar, "Apagar", "LUCES OFF", 3, 2)
boton(marco_estandar, "Automáticas", "LUCES AUTO", 3, 3)

tk.Label(marco_estandar, text="Direccionales:").grid(row=4, column=0, sticky="w")
boton(marco_estandar, "Izquierda", "DIR IZQ", 4, 1)
boton(marco_estandar, "Derecha", "DIR DER", 4, 2)
boton(marco_estandar, "Emergencia", "DIR EMERGENCIA", 4, 3)
boton(marco_estandar, "Apagar", "DIR OFF", 5, 1)

tk.Label(marco_estandar, text="Patrones:").grid(row=6, column=0, sticky="w")
boton(marco_estandar, "Círculo", "CIRCULO", 6, 1)
boton(marco_estandar, "Infinito", "INFINITO", 6, 2)
boton(marco_estandar, "Zigzag", "ZIGZAG", 6, 3)

boton(marco_estandar, "Leer sensor", "SENSOR", 7, 1)

#Marco del modo decremento ( parte 2 del proyecto )
marco_decremento = tk.Frame(ventana)

tk.Label(marco_decremento, text="Decrementador en 5", font=("Arial", 13, "bold")).pack(pady=5)
tk.Label(marco_decremento, text="Marque los bits de entrada (A es el más significativo):").pack()

a = tk.IntVar()
b = tk.IntVar()
c = tk.IntVar()
marco_bits = tk.Frame(marco_decremento)
marco_bits.pack(pady=5)
tk.Checkbutton(marco_bits, text="A", variable=a, command=mostrar_numero).grid(row=0, column=0, padx=10)
tk.Checkbutton(marco_bits, text="B", variable=b, command=mostrar_numero).grid(row=0, column=1, padx=10)
tk.Checkbutton(marco_bits, text="C", variable=c, command=mostrar_numero).grid(row=0, column=2, padx=10)

numero_texto = tk.Label(marco_decremento, text="Número de entrada: 0")
numero_texto.pack()
tk.Button(marco_decremento, text="Decrementar", width=16, command=decrementar).pack(pady=4)
tk.Button(marco_decremento, text="Probar las 8 combinaciones", width=24, command=probar_todo).pack(pady=4)
resultado_texto = tk.Label(marco_decremento, text="", font=("Courier", 10), justify="left")
resultado_texto.pack()
tk.Label(marco_decremento, text="El resultado (X Y Z) se ve en los LEDs frontales del carro").pack(pady=5)

#Parte de abajo
tk.Button(ventana, text="Reconectar", command=buscar_carrito).pack(side="bottom", pady=5)
estado = tk.Label(ventana, text="", wraplength=480)
estado.pack(side="bottom", pady=5)

marco_estandar.pack(pady=10)
ventana.after(200, buscar_carrito)
ventana.mainloop()