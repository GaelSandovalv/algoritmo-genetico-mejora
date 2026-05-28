# Análisis del algoritmo

Análisis de complejidad (Big O) en tiempo y espacio del algoritmo genético
del proyecto, en sus dos versiones: AG Base y AG Mejorado.

Documento complementario de [`ANALISIS.md`](ANALISIS.md). Para gráficos de
desempeño ver [`GRAFICOS_DESEMPENO.md`](GRAFICOS_DESEMPENO.md); para los
diagramas UML ver [`DIAGRAMAS_UML.md`](DIAGRAMAS_UML.md).

## Notación

- **G** = número de generaciones
- **P** = tamaño de la población
- **L** = longitud del alineamiento (con gaps)
- **S** = número de secuencias
- **k** = tamaño de torneo (constante, k = 3 por defecto)

## Complejidad por operador

| Operador | Complejidad temporal | Notas |
|---|---|---|
| `crear_individuo` | O(S · L) | Inserta gaps en cada fila |
| `crear_poblacion` | O(P · S · L) | P individuos |
| `calcular_fitness` | O(S² · L) | Suma de pares: todos los pares de filas, cada columna |
| `validar_integridad` | O(S · L) | Compara fila sin gaps con la original |
| `seleccion_ruleta` | O(P) | Recorre toda la población acumulando pesos |
| `seleccion_torneo` | O(k) | k muestras y un máximo; k es constante |
| `cruza_un_punto` | O(S · L) | Concatena y rellena hasta longitud objetivo |
| `mutacion_mover_gap` | O(S · L) | Busca un gap y lo mueve a otra posición |
| `mutacion_bloques` | O(S · L) | Insertar / mover / eliminar bloque de gaps |
| `diversidad_poblacion` | O(P · S · L) | Hash de cada individuo en un set |
| `elitismo` (sort + slice) | O(P · log P) | Ordenar la población por fitness |

## Complejidad por generación

**AG Base:**

Cada generación realiza:

- `P` evaluaciones de fitness → O(P · S² · L)
- `P` validaciones de integridad → O(P · S · L)
- `P` selecciones por ruleta + `P` cruzas + ≤ `P` mutaciones → O(P · (P + S · L))

Como `S² · L` domina al resto cuando `S ≥ 2`, el costo por generación es:

```
O(P · S² · L)
```

**AG Mejorado:**

Cada generación realiza lo mismo que el AG Base, más:

- 1 ordenamiento por fitness para el elitismo → O(P · log P)
- Selección por torneo en lugar de ruleta → O(k) por padre, k constante (más barato que ruleta)

Sustituyendo:

```
O(P · S² · L + P · log P)
```

El término `P · log P` es despreciable cuando `S² · L >> log P`. Con los
defaults del proyecto (`P = 40`, `S = 4`, `L ≈ 20`) tenemos `S² · L = 320`
contra `log₂ P ≈ 5`, así que en la práctica el AG Mejorado tiene la misma
clase de complejidad por generación que el AG Base.

## Complejidad total

Ejecutar las `G` generaciones secuencialmente:

```
O(G · P · S² · L)     (ambas versiones)
```

Con los defaults del benchmark (`G = 100`, `P = 40`, `S = 4`, `L ≈ 20`)
esto da del orden de **3.2 × 10⁵ operaciones elementales** por corrida —
consistente con los milisegundos medidos por generación en
[`GRAFICOS_DESEMPENO.md`](GRAFICOS_DESEMPENO.md).

## Complejidad espacial

En cualquier momento se mantienen en memoria:

- La población actual: `P` individuos × `S` filas × `L` caracteres.
- La nueva generación en construcción: hasta `P` individuos más.
- El historial de mejor fitness por generación: `G` números.

```
O(P · S · L + G)
```

Y como típicamente `P · S · L >> G`, la cota práctica es:

```
O(P · S · L)
```

## Comparación

| Aspecto | AG Base | AG Mejorado |
|---|---|---|
| Tiempo por generación | O(P · S² · L) | O(P · S² · L + P · log P) |
| Tiempo total | O(G · P · S² · L) | O(G · P · S² · L) |
| Espacio | O(P · S · L) | O(P · S · L) |
| Operador caro extra | — | Ordenamiento para elitismo |
| Operador barato extra | — | Torneo (vs. ruleta) |

**Conclusión:** ambas versiones comparten la misma clase de complejidad
asintótica, `O(G · P · S² · L)`. El AG Mejorado añade un término
sub-dominante por el sort del elitismo, compensado por una selección por
torneo más barata que la ruleta. La diferencia de desempeño observada en
los benchmarks (ver [`GRAFICOS_DESEMPENO.md`](GRAFICOS_DESEMPENO.md)) no
proviene de hacer menos operaciones por generación, sino de **explorar
mejor** el espacio de soluciones gracias al elitismo y la mayor presión
selectiva del torneo.
