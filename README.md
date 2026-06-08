# Ricochet Robots — Proyecto IA

Agente de búsqueda que resuelve el juego Ricochet Robots.  


---

## Estructura del proyecto

```
ricochet_robots/
├── main.py               # CLI: modos play, solve y benchmark
├── game.py               # Tablero, robots, movimiento y estado del juego
├── algorithms.py         # BFS, DFS, A* y las 5 heurísticas
├── output_writer.py      # Genera output.txt y los CSVs del benchmark
├── levels/
│   ├── level_01_6x6.txt
│   ├── level_02_6x6.txt
│   ├── level_03_6x6.txt
│   ├── level_04_10x10.txt
│   ├── level_05_10x10.txt
│   ├── level_06_10x10.txt
│   ├── level_07_16x16.txt
│   ├── level_08_16x16.txt
│   ├── level_09_16x16.txt
│   ├── level_10_25x25.txt
│   ├── level_11_25x25.txt
│   └── level_12_25x25.txt
├── benchmark_results/    # CSVs generados al correr el benchmark
│   ├── cost_of_path.csv
│   ├── nodos_expandidos.csv
│   ├── profundidad_de_búsqueda.csv
│   ├── max_search_depth.csv
│   ├── running_time.csv
│   └── max_ram_usage.csv
└── README.md
```

---

## Requisitos

- Python 3.10 o superior
- Sin dependencias externas (solo librería estándar)

---

## Cómo usar

### Jugar manualmente

```bash
python main.py play levels/level_01_6x6.txt
```

El juego muestra el tablero en consola. En cada turno:
1. Elige el robot por su ID (`A`, `B`, `C`…) o por su número en la lista
2. Elige la dirección: `U` (arriba), `D` (abajo), `L` (izquierda), `R` (derecha)

El robot se desliza hasta chocar con una pared u otro robot.  
La casilla objetivo aparece marcada con `X` en el tablero.

### Resolver con IA

```bash
# BFS — óptimo en número de movimientos
python main.py solve levels/level_01_6x6.txt --algo bfs

# DFS — más rápido en memoria, no garantiza óptimo
python main.py solve levels/level_01_6x6.txt --algo dfs

# A* — usa heurísticas para guiar la búsqueda (3 heurísticas por defecto)
python main.py solve levels/level_01_6x6.txt --algo astar
```

El resultado se guarda en `output.txt` en el directorio desde donde corres el comando.

### Benchmark completo

```bash
python main.py benchmark --levels-dir levels/ --output-dir benchmark_results/
```

Corre los 10 algoritmos/configuraciones en los 12 niveles y guarda un CSV por métrica en `benchmark_results/`.

---

## Formato de los niveles (.txt)

```
622227        ← tablero fila por fila (un dígito por celda)
100003
103003
150007
100043
544548
1 2 azul      ← robots: fila columna color
2 3 amarillo
5 4 rojo
3 2 azul      ← última línea: fila columna color del destino
```

### Código de celdas

| Número | Significado                  |
|--------|------------------------------|
| 0      | Celda vacía                  |
| 1      | Pared izquierda              |
| 2      | Pared superior               |
| 3      | Pared derecha                |
| 4      | Pared inferior               |
| 5      | Pared izquierda + inferior   |
| 6      | Pared superior + izquierda   |
| 7      | Pared superior + derecha     |
| 8      | Pared inferior + derecha     |
| 9      | Celda bloqueada (no transitable) |

Los bordes del tablero siempre tienen paredes implícitas.  
Si el color del destino es `multicolor`, cualquier robot puede llegar ahí.

---

## Algoritmos implementados

### BFS (Búsqueda en Anchura)

Usa una cola FIFO. Explora nivel por nivel, garantizando encontrar la solución con el **menor número de movimientos**. Consume más memoria en tableros grandes porque mantiene todos los estados del nivel actual en la frontera.

### DFS (Búsqueda en Profundidad)

Usa una pila LIFO. Va lo más profundo posible antes de retroceder. **No garantiza solución óptima** y puede tardar mucho si hay ramas largas sin solución. Tiene un corte automático a 60 segundos.

### A* (A-Star)

Usa una cola de prioridad con `f(n) = g(n) + h(n)`:
- `g(n)` = movimientos reales realizados hasta el estado actual
- `h(n)` = estimación del coste restante (combinación ponderada de heurísticas)

Tiene un corte automático a 60 segundos. Con buenas heurísticas es más eficiente que BFS porque no explora estados que parecen lejos del objetivo.

#### Las 5 heurísticas disponibles

| ID | Nombre               | Descripción |
|----|----------------------|-------------|
| H1 | Manhattan            | Distancia Manhattan del robot objetivo al destino, normalizada por el tamaño del tablero |
| H2 | Línea recta          | Penaliza si el robot no está en la misma fila ni columna que el destino |
| H3 | Robots bloqueantes   | Cuenta robots que están entre el robot objetivo y el destino |
| H4 | Estimación con pared | Versión de H1 escalada 1.3× para compensar obstáculos intermedios |
| H5 | Distancia combinada  | Promedio de distancias Manhattan de todos los robots al destino |

#### Configuraciones del benchmark

| Configuración        | Heurísticas | Pesos |
|----------------------|-------------|-------|
| A* pesos iguales     | H1, H2, H3  | 1/3, 1/3, 1/3 |
| A* configuración 1   | H1, H2, H3  | 0.6, 0.2, 0.2 |
| A* configuración 2   | H1, H2, H3  | 0.4, 0.4, 0.2 |
| A* con 1 heurística  | H1          | 1.0 |
| A* con 2 heurísticas | H1, H2      | 0.5, 0.5 |
| A* con 3 heurísticas | H1, H2, H3  | 1/3, 1/3, 1/3 |
| A* con 4 heurísticas | H1–H4       | 0.25 × 4 |
| A* con 5 heurísticas | H1–H5       | 0.2 × 5 |

---

## Archivo output.txt

Cada corrida de `solve` genera o sobreescribe `output.txt`:

```
path_to_goal: ['A-D', 'A-R']
cost_of_path: 2
nodos_expandidos: 29
profundidad_de_búsqueda: 2
max_search_depth: 4
running_time: 0.00054100
max_ram_usage: 0.02237700
```

- `path_to_goal`: lista de movimientos en formato `RobotID-Dirección` (U/D/L/R)
- `cost_of_path`: total de movimientos (cada movimiento puede deslizar varias casillas)
- `nodos_expandidos`: estados del árbol de búsqueda que se abrieron
- `profundidad_de_búsqueda`: profundidad del nodo solución en el árbol
- `max_search_depth`: la mayor profundidad que alcanzó el algoritmo durante toda la búsqueda
- `running_time`: segundos totales de ejecución
- `max_ram_usage`: pico de memoria RAM en MB (medido con `tracemalloc`)

Si el algoritmo no encuentra solución en 60 segundos, se registra `Timeout` en `cost_of_path`.

---

## Niveles incluidos

| Archivo               | Tamaño | Robots | Dificultad |
|-----------------------|--------|--------|------------|
| level_01_6x6.txt      | 6×6    | 3      | Fácil      |
| level_02_6x6.txt      | 6×6    | 3      | Fácil      |
| level_03_6x6.txt      | 6×6    | 3      | Media      |
| level_04_10x10.txt    | 10×10  | 4      | Media      |
| level_05_10x10.txt    | 10×10  | 4      | Media      |
| level_06_10x10.txt    | 10×10  | 4      | Media-Alta |
| level_07_16x16.txt    | 16×16  | 4      | Alta       |
| level_08_16x16.txt    | 16×16  | 4      | Alta       |
| level_09_16x16.txt    | 16×16  | 4      | Alta       |
| level_10_25x25.txt    | 25×25  | 5      | Muy Alta   |
| level_11_25x25.txt    | 25×25  | 5      | Alta       |
| level_12_25x25.txt    | 25×25  | 5      | Alta       |

Los niveles 10×10 sin obstáculos internos y los 16×16/25×25 grandes pueden exceder el límite de 60s con BFS/DFS. Los resultados `Timeout` en `benchmark_results/` reflejan eso.
