# Formula-E-CES-TEC
Carro a escala controlado con Raspberry Pi Pico W en MicroPython: motores con L298N ( PWM ), luces con registro de corrimiento 74LS164 y encendido automático con fotorresistencia.

=============================
 FORMULA E CES TEC - PROYECTO 
=============================

Curso:    Fundamentos de Sistemas Computacionales
Carrera:  Ingeniería en Computadores
Institución: Tecnológico de Costa Rica (TEC)
Periodo:  II Semestre 2026

Integrantes:
  - Imanol Ovares Monge
  - Alexa Herrera Sánchez

------------------------------------------------------------
1. VERSIÓN DE PYTHON
------------------------------------------------------------
El programa corre en la Raspberry Pi Pico W con MicroPython,
que es compatible con Python 3.4
 
  - Intérprete: MicroPython para Raspberry Pi Pico W
  - IDE: Thonny
 
Para ver la versión de MicroPython, escribir en la consola de Thonny:
  import sys
  print(sys.implementation)

En nuestro caso la versión utilizada es la 1.29.0


--------------------------------------------------------------
2. RUTA DE GIT
--------------------------------------------------------------
https://github.com/imanol1008/formula-e-ces-tec

--------------------------------------------------------------
3. CONEXIONES DE LA RASPBERRY PI PICO W
--------------------------------------------------------------
  Pin físico   GPIO    Conectado a
  ----------   -----   ---------------------------------------
  1            GP0     74LS164, pines 1 y 2 (datos)
  2            GP1     74LS164, pin 8 (reloj)
  4            GP2     L298N IN1 (tracción)
  5            GP3     L298N IN2 (tracción)
  6            GP4     L298N ENA (PWM tracción)
  7            GP5     L298N ENB (dirección)
  9            GP6     L298N IN3 (dirección)
  10           GP7     L298N IN4 (dirección)
  31           GP26    Fotorresistencia (entrada analógica)
  36           3V3     Fotorresistencia (alimentación)
  38           GND     Tierra común del circuito
  39           VSYS    5 V del regulador L7805CV
 
Salidas del registro 74LS164 hacia los LEDs:
  Pin 3 (QA)  Frontal izquierda    Pin 10 (QE)  Direccional izquierda
  Pin 4 (QB)  Frontal derecha      Pin 11 (QF)  Direccional derecha
  Pin 5 (QC)  Trasera izquierda
  Pin 6 (QD)  Trasera derecha

--------------------------------------------------------------
4. OTRAS INDICACIONES (COMANDOS)
--------------------------------------------------------------
 -Luces: Dir Der ( Direccional Derecha ), Dir Izq ( Direccional Izquierda ), Dir Emergencia ( Direccionales de emergencia ), Luces On ( luces frontales y traseras encendidas ), Luces Off ( Luces frontales y traseras apagadas ).

-Movimientos: Atrás, Adelante, Derecha, Izquierda, Recto, Parar.

-Velocidad: Está en escala del 0 al 100, se puede ajustar al escribir el comando y el número de la velocidad deseada.
 
