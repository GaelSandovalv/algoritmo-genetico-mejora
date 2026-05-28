# Diagramas UML

Cuatro diagramas UML del proyecto (en formato **Mermaid**, renderizado
nativamente por GitHub al abrir este archivo en el navegador).

Documento complementario de [`ANALISIS.md`](ANALISIS.md). Para el análisis
del algoritmo ver [`ANALISIS_ALGORITMO.md`](ANALISIS_ALGORITMO.md); para
los gráficos de desempeño ver [`GRAFICOS_DESEMPENO.md`](GRAFICOS_DESEMPENO.md).

## 1. Diagrama de actividad — Flujo del AG Mejorado

Muestra el flujo de control de una corrida completa del AG Mejorado: la
inicialización, el bucle por generación con sus dos lazos anidados
(reproducción hasta completar la población, y avance hasta la última
generación), y los puntos de decisión.

```mermaid
flowchart TD
    Inicio([Inicio]) --> Inicializar[Inicializar población]
    Inicializar --> Evaluar[Calcular fitness de cada individuo]
    Evaluar --> Validar[Validar integridad de cada individuo]
    Validar --> Ordenar[Ordenar población por fitness]
    Ordenar --> Elite[Copiar élite a nueva generación]
    Elite --> SelTorneo[Selección por torneo de 2 padres]
    SelTorneo --> Cruzar[Cruza de un punto]
    Cruzar --> Mutar[Mutación por bloques de gaps]
    Mutar --> Agregar[Agregar hijo a nueva generación]
    Agregar --> Cond1{¿Población completa?}
    Cond1 -- No --> SelTorneo
    Cond1 -- Sí --> Reemplazar[Reemplazar población]
    Reemplazar --> Cond2{¿Última generación?}
    Cond2 -- No --> Evaluar
    Cond2 -- Sí --> Fin([Devolver mejor individuo])
```

## 2. Diagrama de secuencia — Una corrida típica

Muestra las llamadas entre módulos cuando el usuario ejecuta el modo demo
(`python algoritmo_genetico.py` sin flags): `__main__` invoca a
`comparar`, que ejecuta ambos algoritmos uno tras otro y delega el
graficado final a `graficar`.

```mermaid
sequenceDiagram
    actor Usuario
    participant main as __main__
    participant comp as comparar
    participant base as ag_base
    participant mej as ag_mejorado
    participant fit as calcular_fitness
    participant val as validar_integridad
    participant grf as graficar
    Usuario->>main: python algoritmo_genetico.py
    main->>comp: comparar()
    comp->>base: ag_base(originales)
    loop generaciones
        base->>fit: calcular_fitness(individuo)
        base->>val: validar_integridad(individuo)
    end
    base-->>comp: mejor_base, hist_base
    comp->>mej: ag_mejorado(originales)
    loop generaciones
        mej->>fit: calcular_fitness(individuo)
        mej->>val: validar_integridad(individuo)
    end
    mej-->>comp: mejor_mej, hist_mej
    comp->>grf: graficar(hist_base, hist_mej)
    grf-->>Usuario: comparacion_fitness.png
```

## 3. Diagrama de componentes — Módulos lógicos

Aunque el código está en un solo archivo, agrupar las funciones por
responsabilidad clarifica el diseño: entrada/salida, datos, operadores
genéticos, evaluación, algoritmos y visualización.

```mermaid
flowchart LR
    subgraph IO[Entrada/Salida]
        Main[main + argparse]
    end
    subgraph Datos[Generación de datos]
        Gen[generar_secuencias]
    end
    subgraph Ops[Operadores genéticos]
        Sel[seleccion_ruleta / seleccion_torneo]
        Cru[cruza_un_punto]
        Mut[mutacion_mover_gap / mutacion_bloques]
        Eli[elitismo]
    end
    subgraph Eval[Evaluación]
        Fit[calcular_fitness]
        Val[validar_integridad]
    end
    subgraph Alg[Algoritmos]
        Base[ag_base]
        Mej[ag_mejorado]
    end
    subgraph Viz[Visualización y análisis]
        Graf[graficar / graficar_convergencia_promedio / graficar_tiempo / graficar_diversidad / graficar_sensibilidad]
        Bench[ejecutar_benchmark / ejecutar_sensibilidad]
    end
    Main --> Datos
    Main --> Alg
    Main --> Viz
    Alg --> Ops
    Alg --> Eval
    Bench --> Alg
    Viz --> Bench
```

## 4. Diagrama de clases (conceptual)

> **Nota:** Este diagrama representa una **abstracción conceptual del
> dominio**, no la implementación real del código (que está escrita en
> estilo funcional, sin clases). Sirve para discutir las entidades del
> problema y sus relaciones tal como un diseño orientado a objetos las
> organizaría.

```mermaid
classDiagram
    class Individuo {
        +list~str~ alineamiento
        +int fitness
        +validar_integridad() bool
    }
    class Poblacion {
        +list~Individuo~ individuos
        +int generacion
        +diversidad() int
    }
    class OperadorGenetico {
        <<abstract>>
        +aplicar()
    }
    class Seleccion {
        +seleccionar(Poblacion) Individuo
    }
    class Cruza {
        +cruzar(Individuo, Individuo) Individuo
    }
    class Mutacion {
        +mutar(Individuo) Individuo
    }
    class Elitismo {
        +conservar(Poblacion, int) list~Individuo~
    }
    class AlgoritmoGenetico {
        +Poblacion poblacion
        +int generaciones
        +ejecutar() Individuo
    }
    OperadorGenetico <|-- Seleccion
    OperadorGenetico <|-- Cruza
    OperadorGenetico <|-- Mutacion
    OperadorGenetico <|-- Elitismo
    AlgoritmoGenetico --> Poblacion
    AlgoritmoGenetico --> OperadorGenetico
    Poblacion --> Individuo
```
