import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASES = "ACGT"


def generar_secuencias(semilla=42, n=4, longitud_ancestro=12):
    rng = random.Random(semilla)
    ancestro = [rng.choice(BASES) for _ in range(longitud_ancestro)]
    secuencias = []
    for _ in range(n):
        s = list(ancestro)
        for _ in range(rng.randint(1, 2)):
            i = rng.randrange(len(s))
            s[i] = rng.choice(BASES)
        for _ in range(rng.randint(0, 1)):
            if len(s) > 1:
                del s[rng.randrange(len(s))]
        for _ in range(rng.randint(0, 1)):
            s.insert(rng.randrange(len(s) + 1), rng.choice(BASES))
        secuencias.append("".join(s))
    return secuencias


def validar_integridad(individuo, originales):
    if len(individuo) != len(originales):
        return False
    for fila, original in zip(individuo, originales):
        if fila.replace("-", "") != original:
            return False
    return True


def calcular_fitness(individuo):
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
    longitud = max(len(fila) for fila in individuo)
    return [fila + "-" * (longitud - len(fila)) for fila in individuo]


def crear_individuo(originales, longitud, rng):
    individuo = []
    for original in originales:
        fila = list(original)
        for _ in range(longitud - len(fila)):
            fila.insert(rng.randrange(len(fila) + 1), "-")
        individuo.append("".join(fila))
    return individuo


def crear_poblacion(originales, tam_poblacion, longitud, rng):
    return [crear_individuo(originales, longitud, rng)
            for _ in range(tam_poblacion)]


def diversidad_poblacion(poblacion):
    return len({tuple(individuo) for individuo in poblacion})


def seleccion_ruleta(poblacion, fitnesses, rng):
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
    n = len(padre1)
    punto = rng.randint(1, n - 1)
    hijo = padre1[:punto] + padre2[punto:]
    return igualar_longitud(hijo)


def mutacion_mover_gap(individuo, rng):
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
            prob_mutacion=0.3, semilla=1, callback=None):
    rng = random.Random(semilla)
    longitud = max(len(s) for s in originales) + 6
    poblacion = crear_poblacion(originales, tam_poblacion, longitud, rng)
    historial = []
    mejor_global = None
    mejor_fit_global = float("-inf")
    for gen in range(generaciones):
        inicio = time.perf_counter()
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
        tiempo_ms = (time.perf_counter() - inicio) * 1000
        if callback is not None:
            callback(gen, poblacion, fitnesses, tiempo_ms)
        poblacion = nueva
    return mejor_global, historial


def seleccion_torneo(poblacion, fitnesses, rng, tam_torneo=3):
    k = min(tam_torneo, len(poblacion))
    indices = rng.sample(range(len(poblacion)), k)
    mejor = max(indices, key=lambda idx: fitnesses[idx])
    return poblacion[mejor]


def insertar_bloque_gaps(individuo, rng, tam_bloque=3):
    individuo = list(individuo)
    idx = rng.randrange(len(individuo))
    fila = list(individuo[idx])
    pos = rng.randrange(len(fila) + 1)
    for _ in range(tam_bloque):
        fila.insert(pos, "-")
    individuo[idx] = "".join(fila)
    return igualar_longitud(individuo)


def mover_bloque_gaps(individuo, rng, tam_bloque=3):
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
    individuo = igualar_longitud(individuo)
    longitud = len(individuo[0])
    quitar = {c for c in range(longitud)
              if all(fila[c] == "-" for fila in individuo)}
    if not quitar:
        return individuo
    return ["".join(ch for c, ch in enumerate(fila) if c not in quitar)
            for fila in individuo]


def mutacion_bloques(individuo, rng, longitud_maxima):
    operacion = rng.choice(["insertar", "mover", "eliminar"])
    longitud_actual = max(len(f) for f in individuo)
    if operacion == "insertar" and longitud_actual + 3 > longitud_maxima:
        operacion = "eliminar"
    if operacion == "insertar":
        return insertar_bloque_gaps(individuo, rng)
    if operacion == "mover":
        return mover_bloque_gaps(individuo, rng)
    return eliminar_columnas_gaps(individuo)


def ag_mejorado(originales, tam_poblacion=60, generaciones=250,
                prob_mutacion=0.3, semilla=1, num_elite=4, tam_torneo=3,
                callback=None):
    rng = random.Random(semilla)
    longitud_inicial = max(len(s) for s in originales) + 6
    longitud_maxima = 2 * longitud_inicial
    poblacion = crear_poblacion(originales, tam_poblacion,
                                longitud_inicial, rng)
    historial = []
    mejor_global = None
    mejor_fit_global = float("-inf")
    for gen in range(generaciones):
        inicio = time.perf_counter()
        fitnesses = [calcular_fitness(ind) for ind in poblacion]
        for ind in poblacion:
            if not validar_integridad(ind, originales):
                raise ValueError(
                    f"Integridad violada en AG mejorado, generacion {gen}")
        orden = sorted(range(len(poblacion)),
                       key=lambda k: fitnesses[k], reverse=True)
        poblacion = [poblacion[k] for k in orden]
        fitnesses = [fitnesses[k] for k in orden]
        fit_mejor = fitnesses[0]
        historial.append(fit_mejor)
        if fit_mejor > mejor_fit_global:
            mejor_fit_global = fit_mejor
            mejor_global = poblacion[0]
        nueva = list(poblacion[:num_elite])
        while len(nueva) < tam_poblacion:
            p1 = seleccion_torneo(poblacion, fitnesses, rng, tam_torneo)
            p2 = seleccion_torneo(poblacion, fitnesses, rng, tam_torneo)
            hijo = cruza_un_punto(p1, p2, rng)
            if rng.random() < prob_mutacion:
                hijo = mutacion_bloques(hijo, rng, longitud_maxima)
            nueva.append(hijo)
        tiempo_ms = (time.perf_counter() - inicio) * 1000
        if callback is not None:
            callback(gen, poblacion, fitnesses, tiempo_ms)
        poblacion = nueva
    return mejor_global, historial


def mostrar_resultado(nombre, individuo, originales):
    individuo = eliminar_columnas_gaps(individuo)
    print(f"--- {nombre} ---")
    print(f"  Fitness: {calcular_fitness(individuo)}")
    print("  Alineamiento:")
    for i, fila in enumerate(individuo):
        print(f"    S{i + 1}: {fila}")
    ok = validar_integridad(individuo, originales)
    print(f"  Validacion de integridad: {'CORRECTA' if ok else 'FALLIDA'}")
    print()


def graficar(hist_base, hist_mejorado, archivo, mostrar=False):
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
    if mostrar:
        try:
            os.startfile(os.path.abspath(archivo))
        except Exception:
            print("(No se pudo abrir la ventana; abre el archivo manualmente.)")


def comparar(semilla_datos=42, semilla_ag=1, tam_poblacion=40,
             generaciones=100, archivo="comparacion_fitness.png",
             mostrar=True):
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

    graficar(hist_base, hist_mej, archivo, mostrar=mostrar)
    return hist_base, hist_mej


def ejecutar_benchmark(originales, n_corridas=30, tam_poblacion=40,
                       generaciones=100):
    resultado = {
        "base": {"fitness": [], "tiempo": [], "diversidad": []},
        "mejorado": {"fitness": [], "tiempo": [], "diversidad": []},
    }
    for semilla in range(n_corridas):
        for nombre, ag in (("base", ag_base), ("mejorado", ag_mejorado)):
            fits = []
            tiempos = []
            divs = []
            def cb(gen, poblacion, fitnesses, tiempo_ms,
                   _f=fits, _t=tiempos, _d=divs):
                _f.append(max(fitnesses))
                _t.append(tiempo_ms)
                _d.append(diversidad_poblacion(poblacion))
            ag(originales, tam_poblacion=tam_poblacion,
               generaciones=generaciones, semilla=semilla, callback=cb)
            resultado[nombre]["fitness"].append(fits)
            resultado[nombre]["tiempo"].append(tiempos)
            resultado[nombre]["diversidad"].append(divs)
    return resultado


if __name__ == "__main__":
    comparar()
