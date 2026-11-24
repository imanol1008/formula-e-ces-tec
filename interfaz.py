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
def mostrar_panel(panel):
    #Esconde los paneles y muestra solo el que se escogio
    marco_estandar.pack_forget()
    marco_decremento.pack_forget()
    marco_about.pack_forget()
    panel.pack(pady=10)


def modo_estandar():
    if activo:
        activar_decrementador()     #Lo apaga antes de volver al modo estandar
    enviar("MODO ESTANDAR")
    mostrar_panel(marco_estandar)


def modo_decremento():
    mostrar_panel(marco_decremento)


def ver_about():
    mostrar_panel(marco_about)


#Modo decremento
activo = False      #True cuando el decrementador esta encendido


def activar_decrementador():
    #Enciende o apaga el decrementador
    global activo
    if not activo:
        activo = True
        enviar("MODO DECREMENTO")
        boton_activar.config(text="Desactivar decrementador")
        leer_sensor()
    else:
        activo = False
        enviar("MODO ESTANDAR")
        boton_activar.config(text="Activar decrementador")
        resultado_texto.config(text="Decrementador desactivado")


def leer_sensor():
    #Lee la fotorresistencia, la divide en 8 rangos (0 a 7) y manda ese numero al circuito
    if not activo:
        return
    respuesta = enviar("SENSOR")                #La Pico responde por ejemplo "Luz: 57 %"
    if respuesta.startswith("Luz:"):
        luz = int(respuesta.split()[1])         #0 a 100
        numero = min(7, luz * 8 // 100)         #8 rangos de 12,5 % cada uno
        bits = str(numero // 4 % 2) + str(numero // 2 % 2) + str(numero % 2)
        salida = enviar("DEC " + str(numero))   #La Pico pone A, B, C y lee X, Y, Z
        esperado = (numero - 5) % 8
        resultado_texto.config(text="Luz: " + str(luz) + " %  ->  rango " + str(numero) +
                               "  ->  bits A B C = " + bits + "\n" + salida +
                               "\nValor esperado: " + str(esperado))
    ventana.after(1000, leer_sensor)            #Vuelve a leer en 1 segundo


def probar_todo():
    #Le pide a la Pico que pruebe las 8 combinaciones y muestra la tabla
    if not activo:
        enviar("MODO DECREMENTO")
    respuesta = enviar("PRUEBA")
    tabla_texto.config(text=respuesta)
    if not activo:
        enviar("MODO ESTANDAR")
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
tk.Button(marco_modos, text="About", width=16, command=ver_about).grid(row=0, column=2, padx=5)


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
tk.Label(marco_decremento, text="Al activarlo, la entrada (A B C) sale de la fotorresistencia:").pack()
tk.Label(marco_decremento, text="la luz (0 a 100 %) se divide en 8 rangos, del 0 al 7.").pack()
boton_activar = tk.Button(marco_decremento, text="Activar decrementador", width=24, command=activar_decrementador)
boton_activar.pack(pady=6)
resultado_texto = tk.Label(marco_decremento, text="Decrementador desactivado", font=("Arial", 11))
resultado_texto.pack()
tk.Label(marco_decremento, text="Salidas X (MSB), Y y Z (LSB) en los LEDs del carro").pack(pady=5)
tk.Button(marco_decremento, text="Probar las 8 combinaciones", width=24, command=probar_todo).pack(pady=4)
tabla_texto = tk.Label(marco_decremento, text="", font=("Courier", 10), justify="left")
tabla_texto.pack()

#Marco About (Acerca de)
marco_about = tk.Frame(ventana)
carpeta = os.path.dirname(os.path.abspath(__file__))


def integrante(nombre, carne, archivo_foto, columna):
    #Muestra la foto (si existe) y los datos de un integrante
    ruta = os.path.join(carpeta, archivo_foto)
    if os.path.exists(ruta):
        foto = tk.PhotoImage(file=ruta)
        foto = foto.subsample(max(1, foto.width() // 160))   #La achica si es muy grande
        etiqueta = tk.Label(marco_integrantes, image=foto)
        etiqueta.image = foto                                #Para que no se borre la foto
    else:
        etiqueta = tk.Label(marco_integrantes, text="(sin foto)", width=14, height=7)
    etiqueta.grid(row=0, column=columna, padx=20)
    tk.Label(marco_integrantes, text=nombre + "\nCarné " + carne).grid(row=1, column=columna)


tk.Label(marco_about, text="Instituto Tecnológico de Costa Rica", font=("Arial", 12, "bold")).pack()
tk.Label(marco_about, text="Escuela de Ingeniería en Computadores").pack()
tk.Label(marco_about, text="CE1104 Fundamentos de Sistemas Computacionales").pack()
marco_integrantes = tk.Frame(marco_about)
marco_integrantes.pack(pady=8)
integrante("Alexa Herrera Sánchez", "2026011902", "alexa.png", 0)
integrante("Imanol Ovares Monge", "2026010620", "imanol.png", 1)
tk.Label(marco_about, text="Programa: Carrito Fórmula E CES TEC", font=("Arial", 11, "bold")).pack(pady=4)
tk.Label(marco_about, justify="left", text=
         "Guía básica:\n"
         "1. Encienda el carro y espere a que el LED de la Pico quede fijo.\n"
         "2. Conecte la computadora al hotspot del iPhone y presione Reconectar.\n"
         "3. Modo estándar: controle el carro con los botones.\n"
         "4. Modo decremento: presione Activar decrementador y cambie\n"
         "    la luz sobre la fotorresistencia para ver el resultado en los LEDs.").pack()

#Parte de abajo
tk.Button(ventana, text="Reconectar", command=buscar_carrito).pack(side="bottom", pady=5)
estado = tk.Label(ventana, text="", wraplength=480)
estado.pack(side="bottom", pady=5)

marco_estandar.pack(pady=10)
ventana.after(200, buscar_carrito)
ventana.mainloop()
