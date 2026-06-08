import argparse
from game import load_level, print_board
from algorithms import bfs, dfs, astar, run_search
from output_writer import write_output_txt, run_benchmark

def play_mode(filepath: str):
    board, state = load_level(filepath)
    print("=== RICOCHET ROBOTS ===")
    print(f"Meta: Enviar robot '{board.target.color}' a la casilla ({board.target.r}, {board.target.c})\n")
    
    moves = 0
    while not board.is_goal(state):
        print_board(board, state)
        print(f"Movimientos realizados: {moves}")
        for i, r in enumerate(state.robots):
            print(f" [{i}] Robot {r.id} ({r.color}) en ({r.r}, {r.c})")
            
        try:
            r_sel = input("\nSeleccione el ID o número de robot: ").strip().upper()
            if r_sel.isdigit(): robot_idx = int(r_sel)
            else: robot_idx = next((idx for idx, rob in enumerate(state.robots) if rob.id == r_sel), -1)

            if not (0 <= robot_idx < len(state.robots)):
                print("Robot inválido.")
                continue
                
            direction = input("Dirección (U=Arriba, D=Abajo, L=Izquierda, R=Derecha): ").strip().upper()
            if direction not in ['U', 'D', 'L', 'R']:
                print("Dirección inválida.")
                continue
                
            new_state = board.move_robot(state, robot_idx, direction)
            if new_state:
                state = new_state
                moves += 1
            else:
                print("¡Movimiento bloqueado por paredes u otros robots!")
        except (ValueError, IndexError): print("Entrada no reconocida.")
            
    print_board(board, state)
    print(f"¡Felicidades! Has ganado en {moves} movimientos.")

def solve_mode(filepath: str, algo: str):
    board, state = load_level(filepath)
    if algo == 'bfs': results = run_search(bfs, board, state)
    elif algo == 'dfs': results = run_search(dfs, board, state)
    elif algo == 'astar': results = run_search(astar, board, state, num_heuristics=3)
    else: return print("Algoritmo no válido.")
        
    write_output_txt(results)
    if results['path_to_goal']: print(f"Solución hallada con costo: {results['cost_of_path']}. Métricas guardadas en output.txt.")
    else: print("No se encontró solución viable para este nivel.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    p_parse = subparsers.add_parser("play")
    p_parse.add_argument("level")
    s_parse = subparsers.add_parser("solve")
    s_parse.add_argument("level")
    s_parse.add_argument("--algo", choices=["bfs", "dfs", "astar"], required=True)
    b_parse = subparsers.add_parser("benchmark")
    b_parse.add_argument("--levels-dir", required=True)
    b_parse.add_argument("--output-dir", required=True)
    
    args = parser.parse_args()
    if args.command == "play": play_mode(args.level)
    elif args.command == "solve": solve_mode(args.level, args.algo)
    elif args.command == "benchmark": run_benchmark(args.levels_dir, args.output_dir)
