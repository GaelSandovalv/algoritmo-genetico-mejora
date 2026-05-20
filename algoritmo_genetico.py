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


def igualar_longitud(individuo):
    """Rellena cada fila con gaps al final hasta que todas midan lo mismo."""
    longitud = max(len(fila) for fila in individuo)
    return [fila + "-" * (longitud - len(fila)) for fila in individuo]


def crear_individuo(originales, longitud, rng):
    """Crea un individuo insertando gaps al azar en cada secuencia hasta
    alcanzar la longitud indicada. 'longitud' debe ser >= la secuencia
    mas larga.
    """
    individuo = []
    for original in originales:
        fila = list(original)
        for _ in range(longitud - len(fila)):
            fila.insert(rng.randrange(len(fila) + 1), "-")
        individuo.append("".join(fila))
    return individuo


def crear_poblacion(originales, tam_poblacion, longitud, rng):
    """Crea una poblacion de individuos aleatorios."""
    return [crear_individuo(originales, longitud, rng)
            for _ in range(tam_poblacion)]


def seleccion_ruleta(poblacion, fitnesses, rng):
    """Selecciona un individuo con probabilidad proporcional a su fitness.

    Los fitness se desplazan para que todos los pesos sean positivos.
    """
    minimo = min(fitnesses)
    pesos = [f - minimo + 1 for f in fitnesses]
    total = sum(pesos)
    r = rng.uniform(0, total)
    acumulado = 0
    for individuo, peso in zip(poblacion, pesos):
        acumulado += peso
        if acumulado >= r:
            return individuo
    return poblacion[-1]


def cruza_un_punto(padre1, padre2, rng):
    """Cruza con un punto de corte sobre las filas: el hijo toma las
    primeras filas de un padre y el resto del otro. Como cada fila se
    copia intacta de un padre, la integridad se conserva.
    """
    n = len(padre1)
    punto = rng.randint(1, n - 1)
    hijo = padre1[:punto] + padre2[punto:]
    return igualar_longitud(hijo)


def mutacion_mover_gap(individuo, rng):
    """Mueve un solo gap a otra posicion dentro de una fila al azar.
    No cambia la longitud de la fila, asi que la integridad se conserva.
    """
    individuo = list(individuo)
    indices_fila = list(range(len(individuo)))
    rng.shuffle(indices_fila)
    for idx in indices_fila:
        fila = list(individuo[idx])
        posiciones_gap = [k for k, ch in enumerate(fila) if ch == "-"]
        if not posiciones_gap:
            continue
        del fila[rng.choice(posiciones_gap)]
        fila.insert(rng.randrange(len(fila) + 1), "-")
        individuo[idx] = "".join(fila)
        return individuo
    return individuo


def ag_base(originales, tam_poblacion=60, generaciones=250,
            prob_mutacion=0.3, semilla=1):
    """Algoritmo genetico BASE (estandar).

    Seleccion por ruleta, cruza de un punto, mutacion que mueve un gap,
    reemplazo generacional y sin elitismo.

    Devuelve (mejor_individuo_encontrado, historial_de_mejor_fitness).
    El historial guarda el mejor fitness de la poblacion en cada generacion.
    """
    rng = random.Random(semilla)
    longitud = max(len(s) for s in originales) + 6
    poblacion = crear_poblacion(originales, tam_poblacion, longitud, rng)
    historial = []
    mejor_global = None
    mejor_fit_global = float("-inf")
    for gen in range(generaciones):
        fitnesses = [calcular_fitness(ind) for ind in poblacion]
        for ind in poblacion:
            if not validar_integridad(ind, originales):
                raise ValueError(
                    f"Integridad violada en AG base, generacion {gen}")
        idx_mejor = max(range(len(poblacion)), key=lambda k: fitnesses[k])
        fit_mejor = fitnesses[idx_mejor]
        historial.append(fit_mejor)
        if fit_mejor > mejor_fit_global:
            mejor_fit_global = fit_mejor
            mejor_global = poblacion[idx_mejor]
        nueva = []
        while len(nueva) < tam_poblacion:
            p1 = seleccion_ruleta(poblacion, fitnesses, rng)
            p2 = seleccion_ruleta(poblacion, fitnesses, rng)
            hijo = cruza_un_punto(p1, p2, rng)
            if rng.random() < prob_mutacion:
                hijo = mutacion_mover_gap(hijo, rng)
            nueva.append(hijo)
        poblacion = nueva
    return mejor_global, historial


def seleccion_torneo(poblacion, fitnesses, rng, tam_torneo=3):
    """Mejora #2: seleccion por torneo. Toma tam_torneo individuos
    distintos al azar y devuelve el de mayor fitness.
    """
    k = min(tam_torneo, len(poblacion))
    indices = rng.sample(range(len(poblacion)), k)
    mejor = max(indices, key=lambda idx: fitnesses[idx])
    return poblacion[mejor]


def cruza_multipunto(padre1, padre2, rng):
    """Mejora #1: cruza con varios puntos de corte (3 a 5) sobre las
    filas, tomando segmentos alternados de cada padre. Cada fila se copia
    intacta de un padre, asi que la integridad se conserva.
    """
    n = len(padre1)
    max_cortes = min(5, n - 1)
    num_cortes = rng.randint(min(3, max_cortes), max_cortes)
    puntos = sorted(rng.sample(range(1, n), num_cortes))
    hijo = []
    usar_padre1 = True
    inicio = 0
    for punto in puntos + [n]:
        fuente = padre1 if usar_padre1 else padre2
        hijo.extend(fuente[inicio:punto])
        inicio = punto
        usar_padre1 = not usar_padre1
    return igualar_longitud(hijo)
