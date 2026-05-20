"""Algoritmo genetico para alineamiento multiple de secuencias de ADN.

Contiene dos versiones del algoritmo (base y mejorada) y una comparacion
de su fitness. Ejecutar con: python algoritmo_genetico.py
"""
import random

import matplotlib
matplotlib.use("Agg")  # backend sin ventana: guarda la grafica como imagen
import matplotlib.pyplot as plt

BASES = "ACGT"


def generar_secuencias(semilla=42, n=6, longitud_ancestro=16):
    """Genera n secuencias de ADN derivadas de un ancestro comun.

    Cada secuencia se obtiene aplicando sustituciones e indels al ancestro.
    Con la misma semilla siempre devuelve el mismo resultado.
    """
    rng = random.Random(semilla)
    ancestro = [rng.choice(BASES) for _ in range(longitud_ancestro)]
    secuencias = []
    for _ in range(n):
        s = list(ancestro)
        for _ in range(rng.randint(2, 3)):          # sustituciones
            i = rng.randrange(len(s))
            s[i] = rng.choice(BASES)
        for _ in range(rng.randint(0, 2)):          # eliminaciones
            if len(s) > 1:
                del s[rng.randrange(len(s))]
        for _ in range(rng.randint(0, 2)):          # inserciones
            s.insert(rng.randrange(len(s) + 1), rng.choice(BASES))
        secuencias.append("".join(s))
    return secuencias


def validar_integridad(individuo, originales):
    """Comprueba que al quitar los gaps de cada fila se recupera la
    secuencia original. Devuelve True solo si todas las filas coinciden.
    """
    if len(individuo) != len(originales):
        return False
    for fila, original in zip(individuo, originales):
        if fila.replace("-", "") != original:
            return False
    return True


def calcular_fitness(individuo):
    """Calcula el fitness de un alineamiento con la suma de pares.

    Por cada par de filas y cada columna: +1 coincidencia, -1 desajuste,
    -2 si una es gap, 0 si ambas son gap. Todas las filas deben tener
    la misma longitud.
    """
    n = len(individuo)
    if n == 0:
        return 0
    longitud = len(individuo[0])
    puntaje = 0
    for i in range(n):
        for j in range(i + 1, n):
            for c in range(longitud):
                a = individuo[i][c]
                b = individuo[j][c]
                if a == "-" and b == "-":
                    puntaje += 0
                elif a == "-" or b == "-":
                    puntaje += -2
                elif a == b:
                    puntaje += 1
                else:
                    puntaje += -1
    return puntaje
