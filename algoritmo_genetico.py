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


def insertar_bloque_gaps(individuo, rng, tam_bloque=3):
    """Inserta un bloque de gaps en una fila al azar. Las demas filas se
    rellenan con gaps finales para igualar la longitud.
    """
    individuo = list(individuo)
    idx = rng.randrange(len(individuo))
    fila = list(individuo[idx])
    pos = rng.randrange(len(fila) + 1)
    for _ in range(tam_bloque):
        fila.insert(pos, "-")
    individuo[idx] = "".join(fila)
    return igualar_longitud(individuo)


def mover_bloque_gaps(individuo, rng, tam_bloque=3):
    """Mueve un bloque contiguo de gaps a otra posicion dentro de la
    misma fila. No cambia la longitud de la fila.
    """
    individuo = list(individuo)
    indices = list(range(len(individuo)))
    rng.shuffle(indices)
    for idx in indices:
        fila = individuo[idx]
        bloques = []
        k = 0
        while k < len(fila):
            if fila[k] == "-":
                inicio = k
                while k < len(fila) and fila[k] == "-":
                    k += 1
                bloques.append((inicio, k - inicio))
            else:
                k += 1
        if not bloques:
            continue
        inicio, longitud = rng.choice(bloques)
        mover = min(tam_bloque, longitud)
        lista = list(fila)
        del lista[inicio:inicio + mover]
        nueva_pos = rng.randrange(len(lista) + 1)
        for _ in range(mover):
            lista.insert(nueva_pos, "-")
        individuo[idx] = "".join(lista)
        return individuo
    return individuo


def eliminar_columnas_gaps(individuo):
    """Elimina las columnas que son gap en todas las filas (compactacion)."""
    individuo = igualar_longitud(individuo)
    longitud = len(individuo[0])
    quitar = {c for c in range(longitud)
              if all(fila[c] == "-" for fila in individuo)}
    if not quitar:
        return individuo
    return ["".join(ch for c, ch in enumerate(fila) if c not in quitar)
            for fila in individuo]


def mutacion_bloques(individuo, rng, longitud_maxima):
    """Mejora #4: mutacion por bloques de gaps. Elige al azar entre
    insertar un bloque, mover un bloque o eliminar columnas de solo gaps.
    Si el individuo ya alcanzo longitud_maxima, compacta en lugar de
    insertar para no crecer sin control.
    """
    operacion = rng.choice(["insertar", "mover", "eliminar"])
    longitud_actual = max(len(f) for f in individuo)
    # insertar_bloque_gaps anade 3 gaps: si eso superaria el limite, compactar
    if operacion == "insertar" and longitud_actual + 3 > longitud_maxima:
        operacion = "eliminar"
    if operacion == "insertar":
        return insertar_bloque_gaps(individuo, rng)
    if operacion == "mover":
        return mover_bloque_gaps(individuo, rng)
    return eliminar_columnas_gaps(individuo)


def ag_mejorado(originales, tam_poblacion=60, generaciones=250,
                prob_mutacion=0.3, semilla=1, num_elite=4,
                tam_torneo=3, paciencia=20):
    """Algoritmo genetico MEJORADO con seis mejoras:

    1. Cruza multipunto (3 a 5 puntos de corte).
    2. Seleccion por torneo.
    3. Criterio de eliminacion: solo la mejor mitad se reproduce.
    4. Mutacion por bloques de gaps.
    5. Inmigrantes aleatorios cuando hay estancamiento.
    6. Elitismo: los mejores pasan intactos y tienen cruza garantizada.

    Devuelve (mejor_individuo_encontrado, historial_de_mejor_fitness).
    """
    rng = random.Random(semilla)
    longitud_inicial = max(len(s) for s in originales) + 6
    longitud_maxima = 2 * longitud_inicial
    poblacion = crear_poblacion(originales, tam_poblacion,
                                longitud_inicial, rng)
    historial = []
    mejor_global = None
    mejor_fit_global = float("-inf")
    generaciones_sin_mejora = 0
    for gen in range(generaciones):
        fitnesses = [calcular_fitness(ind) for ind in poblacion]
        for ind in poblacion:
            if not validar_integridad(ind, originales):
                raise ValueError(
                    f"Integridad violada en AG mejorado, generacion {gen}")
        # ordenar la poblacion de mejor a peor fitness
        orden = sorted(range(len(poblacion)),
                       key=lambda k: fitnesses[k], reverse=True)
        poblacion = [poblacion[k] for k in orden]
        fitnesses = [fitnesses[k] for k in orden]
        fit_mejor = fitnesses[0]
        historial.append(fit_mejor)
        if fit_mejor > mejor_fit_global:
            mejor_fit_global = fit_mejor
            mejor_global = poblacion[0]
            generaciones_sin_mejora = 0
        else:
            generaciones_sin_mejora += 1
        # Mejora #3: solo la mejor mitad se usa como reserva de padres
        reserva = poblacion[:max(2, tam_poblacion // 2)]
        reserva_fit = fitnesses[:len(reserva)]
        # Mejora #6: elitismo - los mejores pasan intactos
        nueva = list(poblacion[:num_elite])
        # Mejora #6: cada elite tiene cruza garantizada
        for elite in poblacion[:num_elite]:
            pareja = seleccion_torneo(reserva, reserva_fit, rng, tam_torneo)
            hijo = cruza_multipunto(elite, pareja, rng)
            if rng.random() < prob_mutacion:
                hijo = mutacion_bloques(hijo, rng, longitud_maxima)
            nueva.append(hijo)
        # Mejora #5: inmigrantes aleatorios si hay estancamiento
        if generaciones_sin_mejora >= paciencia:
            for _ in range(tam_poblacion // 5):
                nueva.append(crear_individuo(originales,
                                             longitud_inicial, rng))
            generaciones_sin_mejora = 0
        # rellenar el resto con cruza y mutacion
        while len(nueva) < tam_poblacion:
            p1 = seleccion_torneo(reserva, reserva_fit, rng, tam_torneo)
            p2 = seleccion_torneo(reserva, reserva_fit, rng, tam_torneo)
            hijo = cruza_multipunto(p1, p2, rng)
            if rng.random() < prob_mutacion:
                hijo = mutacion_bloques(hijo, rng, longitud_maxima)
            nueva.append(hijo)
        poblacion = nueva[:tam_poblacion]
    return mejor_global, historial


def mostrar_resultado(nombre, individuo, originales):
    """Imprime el fitness, el alineamiento y la validacion de integridad.

    Compacta el alineamiento (quita columnas de solo gaps) antes de
    mostrarlo: esas columnas no aportan al fitness y solo estorban a la
    lectura. Quitarlas no altera el fitness ni la integridad.
    """
    individuo = eliminar_columnas_gaps(individuo)
    print(f"--- {nombre} ---")
    print(f"  Fitness: {calcular_fitness(individuo)}")
    print("  Alineamiento:")
    for i, fila in enumerate(individuo):
        print(f"    S{i + 1}: {fila}")
    ok = validar_integridad(individuo, originales)
    print(f"  Validacion de integridad: {'CORRECTA' if ok else 'FALLIDA'}")
    print()


def graficar(hist_base, hist_mejorado, archivo):
    """Genera la grafica de comparacion del fitness y la guarda."""
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(hist_base) + 1), hist_base,
             label="AG Base", color="#d62728")
    plt.plot(range(1, len(hist_mejorado) + 1), hist_mejorado,
             label="AG Mejorado", color="#2ca02c")
    plt.xlabel("Generacion")
    plt.ylabel("Mejor fitness")
    plt.title("Comparacion de fitness: AG Base vs AG Mejorado")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(archivo, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"Grafica guardada en: {archivo}")


def comparar(semilla_datos=42, semilla_ag=1, tam_poblacion=60,
             generaciones=250, archivo="comparacion_fitness.png"):
    """Ejecuta el AG base y el mejorado con los mismos datos y parametros,
    imprime los resultados y genera la grafica de comparacion.

    Devuelve (historial_base, historial_mejorado).
    """
    originales = generar_secuencias(semilla_datos)
    print("Secuencias de ADN generadas:")
    for i, s in enumerate(originales):
        print(f"  S{i + 1}: {s}")
    print()

    mejor_base, hist_base = ag_base(originales, tam_poblacion,
                                    generaciones, semilla=semilla_ag)
    mostrar_resultado("AG BASE", mejor_base, originales)

    mejor_mej, hist_mej = ag_mejorado(originales, tam_poblacion,
                                      generaciones, semilla=semilla_ag)
    mostrar_resultado("AG MEJORADO", mejor_mej, originales)

    fit_base = calcular_fitness(igualar_longitud(mejor_base))
    fit_mej = calcular_fitness(igualar_longitud(mejor_mej))
    if fit_base != 0:
        mejora = (fit_mej - fit_base) / abs(fit_base) * 100
        texto_mejora = f"{mejora:+.1f}%"
    else:
        texto_mejora = "no calculable (fitness base = 0)"
    print("=== COMPARACION ===")
    print(f"  Fitness AG Base:     {fit_base}")
    print(f"  Fitness AG Mejorado: {fit_mej}")
    print(f"  Mejora: {texto_mejora}")
    print()

    graficar(hist_base, hist_mej, archivo)
    return hist_base, hist_mej


if __name__ == "__main__":
    comparar()
