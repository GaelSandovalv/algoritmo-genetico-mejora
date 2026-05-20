# Algoritmo Genético para Alineamiento de Secuencias de ADN

Implementación de un algoritmo genético en dos versiones —**base** y
**mejorada**— para resolver el problema de **alineamiento múltiple de
secuencias de ADN**, con una gráfica que compara el fitness de ambas.

## ¿Qué es un algoritmo genético?

Un algoritmo genético imita la evolución natural. Parte de una *población*
de soluciones candidatas, evalúa su *fitness* (qué tan buena es cada una) y
genera nuevas generaciones mediante **selección** (elegir los mejores como
padres), **cruza** (combinar dos padres) y **mutación** (cambios aleatorios
pequeños). Generación tras generación, el fitness tiende a mejorar.

## El problema: alineamiento de secuencias

Cada *individuo* es un alineamiento de 6 secuencias de ADN con gaps (`-`)
insertados. El **fitness** usa la suma de pares: por cada par de filas y
cada columna suma +1 si coinciden, -1 si difieren y -2 si una es gap.

## Validación de integridad

La cruza y la mutación **solo insertan, mueven o borran gaps**; nunca
alteran ni reordenan las letras A/C/G/T. La función `validar_integridad`
comprueba en cada generación que, al quitar los gaps de cada fila, se
recupera exactamente la secuencia original.

## Las 6 mejoras del algoritmo mejorado

1. **Cruza multipunto:** de 1 punto de corte a 3-5 puntos.
2. **Selección por torneo:** mejor presión selectiva que la ruleta.
3. **Criterio de eliminación:** solo la mejor mitad se reproduce.
4. **Mutación por bloques de gaps:** insertar, mover o eliminar columnas
   de solo gaps.
5. **Inmigrantes aleatorios:** individuos nuevos cuando hay estancamiento.
6. **Elitismo:** los mejores pasan intactos y tienen cruza garantizada.

## Cómo ejecutar

```
pip install -r requirements.txt
python algoritmo_genetico.py
```

El programa imprime las secuencias, los resultados de ambos algoritmos, la
comparación de fitness y genera `comparacion_fitness.png`.

## Resultados

![Comparación de fitness](comparacion_fitness.png)

## Video de demostración

🎥 Link del video: _PENDIENTE_

## Repositorio

🔗 Link de GitHub: https://github.com/GaelSandovalv/algoritmo-genetico-mejora

## Fuentes

- Genetic algorithm — Wikipedia: https://en.wikipedia.org/wiki/Genetic_algorithm
- Naturally selecting solutions: genetic algorithms in bioinformatics — PMC:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3813526/
- SAGA: Sequence Alignment by Genetic Algorithm — Nucleic Acids Research:
  https://academic.oup.com/nar/article/24/8/1515/2359898
