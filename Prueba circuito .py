# Prueba y diagnóstico del decrementador (ABC - 5) en protoboard
# Raspberry Pi Pico W - MicroPython (Thonny)
# Al ejecutarlo recorre las 8 combinaciones de ABC, muestra la tabla
# leída vs. esperada y, si algo falla, imprime el diagnóstico.

import machine, time

# ---------- Pines ----------
A = machine.Pin(4, machine.Pin.OUT)
B = machine.Pin(5, machine.Pin.OUT)
C = machine.Pin(6, machine.Pin.OUT)

X = machine.Pin(7, machine.Pin.IN)   #Sin pull-down
Y = machine.Pin(8, machine.Pin.IN)
Z = machine.Pin(9, machine.Pin.IN)

LECTURAS = 10        #Lecturas por salida para revisar estabilidad
PAUSA = 0.15         #Segundos para que se estabilicen los chips


#Lógica esperada
def esperado(a, b, c):
    nc = 1 - c
    t1 = (1 - a) & c
    t2 = nc & (a ^ b)
    return (t1 | t2, 1 - (b ^ c), nc)


def poner(a, b, c):
    A.value(a); B.value(b); C.value(c)
    time.sleep(PAUSA)


def leer(pin):
    """Lee varias veces. Devuelve (valor, estable)."""
    unos = 0
    for _ in range(LECTURAS):
        unos += pin.value()
        time.sleep_ms(2)
    if unos == 0:
        return 0, True
    if unos == LECTURAS:
        return 1, True
    return (1 if unos * 2 >= LECTURAS else 0), False


#Diagnóstico
def diagnostico(tabla):
    print()
    print("===== DIAGNÓSTICO =====")
    nombres = ("X", "Y", "Z")

    for i, nom in enumerate(nombres):
        leidos = [f[3][i] for f in tabla]
        esperados = [f[4][i] for f in tabla]
        malas = ["{}{}{}".format(f[0], f[1], f[2])
                 for f in tabla if f[3][i] != f[4][i]]
        inest = [f for f in tabla if nom in f[5]]

        if not malas and not inest:
            print("- {}: correcta en las 8 filas.".format(nom))
            continue

        print("- {}: falla en ABC = {}".format(nom, ", ".join(malas) if malas else "-"))
        if all(v == 0 for v in leidos):
            print("    Siempre 0: cable a la Pico suelto, divisor mal armado,")
            print("    o el chip que la genera sin alimentación.")
        elif all(v == 1 for v in leidos):
            print("    Siempre 1: revisa que el cable no esté en el riel de 5 V")
            print("    o en una entrada que esté flotando.")
        elif all(l != e for l, e in zip(leidos, esperados)):
            print("    Sale invertida en todas las filas: estás leyendo el nodo")
            print("    de antes (o después) de un NOT.")
        if inest:
            print("    Lecturas inestables: cable flojo o pin flotando.")

    if all(f[3][0] == 1 - f[3][1] for f in tabla):
        print()
        print("* X leída es el inverso exacto de Y leída en las 8 filas.")
        print("  Muy probable: el cable de X (GP7) está en la fila de B xor C")
        print("  (74LS86 pin 6 / 74LS04 pin 5) en vez del 74LS32 pin 3.")

    yA0 = [f[3][1] for f in tabla if f[0] == 0]
    yA1 = [f[3][1] for f in tabla if f[0] == 1]
    if yA0 != yA1:
        print()
        print("* Y cambia según A, pero Y = NOT(B xor C) no usa A.")
        print("  A se está colando en ese camino: revisa que 74LS86 pin 4 reciba B")
        print("  (no A ni A xor B) y que ningún cable esté una fila corrido.")


#Prueba
print()
print("A B C | X Y Z leido | X Y Z esperado | resultado")
print("------+-------------+----------------+----------")

tabla = []
correctas = 0
for n in range(8):
    a, b, c = (n >> 2) & 1, (n >> 1) & 1, n & 1
    poner(a, b, c)

    lx, ex_ = leer(X)
    ly, ey_ = leer(Y)
    lz, ez_ = leer(Z)
    leido = (lx, ly, lz)
    inest = [nom for nom, ok in (("X", ex_), ("Y", ey_), ("Z", ez_)) if not ok]

    esp = esperado(a, b, c)
    ok = leido == esp and not inest
    if ok:
        correctas += 1
    tabla.append((a, b, c, leido, esp, inest))

    marca = "OK" if ok else "ERROR"
    if inest:
        marca += "  (inestable: " + ",".join(inest) + ")"
    print("{} {} {} |    {} {} {}    |     {} {} {}      | {}".format(
        a, b, c, *leido, *esp, marca))

print()
print("Resultado: {}/8 correctas".format(correctas))
if correctas < 8:
    diagnostico(tabla)

poner(0, 0, 0)