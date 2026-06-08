import os
import csv
from typing import Dict, Any

def write_output_txt(results: Dict[str, Any], filename: str = "output.txt"):
    with open(filename, 'w', encoding='utf-8') as f:
        if results.get('status') == 'Success' and results.get('path_to_goal'):
            f.write(f"path_to_goal: {results['path_to_goal']}\n")
            f.write(f"cost_of_path: {results['cost_of_path']}\n")
        else:
            f.write("path_to_goal: No solution found / Inviable\n")
            f.write("cost_of_path: Inviable\n")
        f.write(f"nodos_expandidos: {results['nodos_expandidos']}\n")
        f.write(f"profundidad_de_búsqueda: {results['profundidad_de_búsqueda']}\n")
        f.write(f"max_search_depth: {results['max_search_depth']}\n")
        f.write(f"running_time: {results['running_time']:.8f}\n")
        f.write(f"max_ram_usage: {results['max_ram_usage']:.8f}\n")

def run_benchmark(levels_dir: str, output_dir: str):
    from game import load_level
    from algorithms import bfs, dfs, astar, run_search
    
    os.makedirs(output_dir, exist_ok=True)
    level_files = sorted([f for f in os.listdir(levels_dir) if f.endswith('.txt')])
    
    configs = {
        "DFS": lambda b, s: run_search(dfs, b, s),
        "BFS": lambda b, s: run_search(bfs, b, s),
        "A* pesos iguales": lambda b, s: run_search(astar, b, s, num_heuristics=3, weights=[1/3, 1/3, 1/3]),
        "A* configuracion 1": lambda b, s: run_search(astar, b, s, num_heuristics=3, weights=[0.6, 0.2, 0.2]),
        "A* configuracion 2": lambda b, s: run_search(astar, b, s, num_heuristics=3, weights=[0.4, 0.4, 0.2]),
        "A* con 1 heuristica": lambda b, s: run_search(astar, b, s, num_heuristics=1, weights=[1.0]),
        "A* con 2 heuristicas": lambda b, s: run_search(astar, b, s, num_heuristics=2, weights=[0.5, 0.5]),
        "A* con 3 heuristicas": lambda b, s: run_search(astar, b, s, num_heuristics=3, weights=[1/3, 1/3, 1/3]),
        "A* con 4 heuristicas": lambda b, s: run_search(astar, b, s, num_heuristics=4, weights=[0.25, 0.25, 0.25, 0.25]),
        "A* con 5 heuristicas": lambda b, s: run_search(astar, b, s, num_heuristics=5, weights=[0.2, 0.2, 0.2, 0.2, 0.2])
    }

    metrics = ["cost_of_path", "nodos_expandidos", "profundidad_de_búsqueda", "max_search_depth", "running_time", "max_ram_usage"]
    results_by_metric = {m: {c: [] for c in configs} for m in metrics}

    for lvl in level_files:
        filepath = os.path.join(levels_dir, lvl)
        print(f"Evaluando nivel: {lvl}")
        for conf_name, conf_func in configs.items():
            board, state = load_level(filepath)
            try:
                res = conf_func(board, state)
                for m in metrics: results_by_metric[m][conf_name].append(res[m])
            except Exception as e:
                for m in metrics: results_by_metric[m][conf_name].append("Error")

    for m in metrics:
        csv_path = os.path.join(output_dir, f"{m}.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Algoritmo"] + level_files)
            for conf_name in configs.keys():
                row = [conf_name]
                for val in results_by_metric[m][conf_name]:
                    if isinstance(val, float): row.append(f"{val:.6f}")
                    else: row.append(str(val))
                writer.writerow(row)
    print(f"Tablas CSV generadas exitosamente en la carpeta '{output_dir}'.")
