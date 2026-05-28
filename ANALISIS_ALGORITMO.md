# Análisis del algoritmo

Descripción del problema, pseudocódigo de las dos versiones del algoritmo
genético y análisis de complejidad teórica (Big O).

Documento complementario de [`ANALISIS.md`](ANALISIS.md), enfocado solo en
el algoritmo. Para gráficos ver [`GRAFICOS_DESEMPENO.md`](GRAFICOS_DESEMPENO.md);
para diagramas UML ver [`DIAGRAMAS_UML.md`](DIAGRAMAS_UML.md).

## 1. Problema

**Alineamiento múltiple de secuencias de ADN.** Dadas `S = 4` secuencias
cortas sobre el alfabeto `{A, C, G, T}`, encontrar un alineamiento (matriz
de filas `S × L` con gaps `-`) que maximice una métrica de similitud
columna por columna. Restricción dura: al quitar los gaps de cada fila se
debe recuperar exactamente la secuencia original (validado en cada
generación por `validar_integridad`).

**Función de fitness (suma de pares):** por cada par de filas `(i, j)` y
cada columna `c`:

- `+1` si ambas letras coinciden y no son gap.
- `-1` si las letras difieren y no son gap.
- `-2` si exactamente una de las dos es gap.
- `0` si ambas son gap.

El fitness total es la suma sobre todos los pares y columnas. Es negativo
cuando el alineamiento es malo, y crece (puede ser positivo) cuando hay
muchas coincidencias.

## 2. Pseudocódigo

### 2.1 AG Base

```
funcion ag_base(originales, tam_poblacion, generaciones, prob_mutacion):
    poblacion := crear_poblacion(originales, tam_poblacion, longitud_fija)
    historial := []
    para gen en 0 .. generaciones - 1:
        fitnesses := [calcular_fitness(ind) para ind en poblacion]
        validar_integridad(cada individuo)
        historial.append(max(fitnesses))
        nueva := []
        mientras |nueva| < tam_poblacion:
            p1 := seleccion_ruleta(poblacion, fitnesses)
            p2 := seleccion_ruleta(poblacion, fitnesses)
            hijo := cruza_un_punto(p1, p2)
            si random() < prob_mutacion:
                hijo := mutacion_mover_gap(hijo)
            nueva.append(hijo)
        poblacion := nueva
    devolver mejor_individuo_global, historial
```

### 2.2 AG Mejorado

Tres diferencias respecto al base: **selección por torneo**, **mutación
por bloques de gaps** y **elitismo**.

```
funcion ag_mejorado(originales, tam_poblacion, generaciones,
                    prob_mutacion, num_elite, tam_torneo):
    poblacion := crear_poblacion(originales, tam_poblacion, longitud_inicial)
    longitud_maxima := 2 * longitud_inicial
    historial := []
    para gen en 0 .. generaciones - 1:
        fitnesses := [calcular_fitness(ind) para ind en poblacion]
        validar_integridad(cada individuo)
        ordenar poblacion y fitnesses por fitness descendente
        historial.append(fitnesses[0])
        nueva := poblacion[0 .. num_elite - 1]    # elitismo
        mientras |nueva| < tam_poblacion:
            p1 := seleccion_torneo(poblacion, fitnesses, tam_torneo)
            p2 := seleccion_torneo(poblacion, fitnesses, tam_torneo)
            hijo := cruza_un_punto(p1, p2)
            si random() < prob_mutacion:
                hijo := mutacion_bloques(hijo, longitud_maxima)
            nueva.append(hijo)
        poblacion := nueva
    devolver mejor_individuo_global, historial
```

**`mutacion_bloques`** elige aleatoriamente entre tres operadores:

- `insertar_bloque_gaps`: inserta un bloque corto de gaps en una posición
  aleatoria de una fila (respetando `longitud_maxima`).
- `mover_bloque_gaps`: localiza un bloque de gaps consecutivos y lo
  reubica dentro de la misma fila.
- `eliminar_columnas_gaps`: elimina las columnas que son `-` en todas las
  filas (limpieza que acorta el alineamiento sin alterar contenido).

**`seleccion_torneo`** toma `tam_torneo` individuos al azar y devuelve el
de mayor fitness — presión selectiva controlable por `tam_torneo`.

## 3. Complejidad teórica (Big O)

Notación:

- **G** = número de generaciones
- **P** = tamaño de la población
- **L** = longitud del alineamiento (con gaps)
- **S** = número de secuencias

| Operador | Complejidad temporal | Notas |
|---|---|---|
| `crear_individuo` | O(S · L) | Inserta gaps en cada fila |
| `crear_poblacion` | O(P · S · L) | P individuos |
| `calcular_fitness` | O(S² · L) | Todos los pares de filas, cada columna |
| `validar_integridad` | O(S · L) | Compara fila sin gaps con original |
| `seleccion_ruleta` | O(P) | Recorre toda la población |
| `seleccion_torneo` | O(k) con k = tam_torneo | k pequeño y constante |
| `cruza_un_punto` | O(S · L) | Concatena y rellena |
| `mutacion_mover_gap` | O(S · L) | Busca gap, lo mueve |
| `mutacion_bloques` | O(S · L) | Insertar / mover / eliminar bloque |
| `elitismo` (sort + slice) | O(P · log P) | Ordenar la población |

**Por generación — AG Base:**
`O(P · S² · L)`. Domina la evaluación de `calcular_fitness` aplicada a las
`P` soluciones.

**Por generación — AG Mejorado:**
`O(P · S² · L + P · log P)`. Igual que el base más el ordenamiento que el
elitismo requiere. Cuando `S² · L >> log P` el término del sort es
despreciable.

**Total (ambos):**
`O(G · P · S² · L)`.

**Complejidad espacial:**
`O(P · S · L)` — la población completa más una nueva generación en
construcción.

## 4. Decisiones de diseño

- **Longitud constante por generación.** El AG Base fija `L = max(|sᵢ|) + 6`
  desde el inicio. El AG Mejorado parte igual, pero permite crecer hasta
  `2 · L_inicial` para que `insertar_bloque_gaps` tenga margen sin violar
  integridad; la limpieza `eliminar_columnas_gaps` impide que el
  alineamiento se infle indefinidamente.
- **Función de fitness con penalización fuerte por gap-letra (`-2`).**
  Castiga columnas mal alineadas más fuerte que las simples discrepancias
  (`-1`), empujando al algoritmo a buscar columnas conservadas.
- **Reproducibilidad.** Toda la aleatoriedad pasa por `random.Random(semilla)`,
  permitiendo correr la misma semilla y obtener bit-a-bit la misma
  trayectoria — base para los benchmarks repetibles del estudio empírico.
