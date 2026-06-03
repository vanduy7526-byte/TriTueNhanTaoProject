import tkinter as tk
from collections import deque
import heapq
import random

# ==========================================
# 1. CẤU TRÚC NODE & HÀM BỔ TRỢ
# ==========================================
def make_move(node, action):
    state = list(node['state'])
    idx = state.index(0)
    r, c = idx // 3, idx % 3

    if action == 'U':
        dr, dc = -1, 0
    elif action == 'D':
        dr, dc = 1, 0
    elif action == 'L':
        dr, dc = 0, -1
    elif action == 'R':
        dr, dc = 0, 1

    new_idx = (r + dr) * 3 + (c + dc)
    state[idx], state[new_idx] = state[new_idx], state[idx]

    return {
        'state': tuple(state),
        'parent': node,
        'action': action,
        'path_cost': node['path_cost'] + 1
    }


def get_moves(state):
    moves = []
    idx = state.index(0)
    r, c = idx // 3, idx % 3
    if r > 0: moves.append('U')
    if r < 2: moves.append('D')
    if c > 0: moves.append('L')
    if c < 2: moves.append('R')
    return moves


def trace_path(node):
    path = []
    while node:
        path.append(node)
        node = node['parent']
    return path[::-1]

def get_diff(state, goal):
    return sum(1 for i in range(9) if state[i] != 0 and state[i] != goal[i])

def manhattan(state, goal):
    dist = 0
    for i in range(9):
        val = state[i]
        if val != 0:
            goal_idx = goal.index(val)
            curr_r, curr_c = i // 3, i % 3
            goal_r, goal_c = goal_idx // 3, goal_idx % 3
            dist += abs(curr_r - goal_r) + abs(curr_c - goal_c)
    return dist

def inversions(state):
    inv_count = 0
    state_list = [x for x in state if x != 0]
    for i in range(len(state_list)):
        for j in range(i + 1, len(state_list)):
            if state_list[i] > state_list[j]:
                inv_count += 1
    return inv_count

def is_cycle(node):
    curr = node['parent']
    while curr:
        if curr['state'] == node['state']: return True
        curr = curr['parent']
    return False


# ==========================================
# 2. CÁC THUẬT TOÁN TÌM KIẾM
# ==========================================

def bfs(puzzle):
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}
    history = []

    if start['state'] == puzzle['goal']:
        history.append(start)
        return trace_path(start), history

    frontier = deque([start])
    in_frontier = {start['state']}
    explored = set()

    while frontier:
        node = frontier.popleft()
        in_frontier.remove(node['state'])
        explored.add(node['state'])
        history.append(node)

        for action in get_moves(node['state']):
            child = make_move(node, action)

            if child['state'] == puzzle['goal']:
                history.append(child)
                return trace_path(child), history

            if child['state'] not in explored and child['state'] not in in_frontier:
                frontier.append(child)
                in_frontier.add(child['state'])

    return [], history


def dfs(puzzle):
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}
    history = []

    if start['state'] == puzzle['goal']:
        history.append(start)
        return trace_path(start), history

    frontier = [start]
    in_frontier = {start['state']}
    explored = set()

    while frontier:
        node = frontier.pop()
        in_frontier.remove(node['state'])
        explored.add(node['state'])
        history.append(node)

        for action in get_moves(node['state']):
            child = make_move(node, action)

            if child['state'] == puzzle['goal']:
                history.append(child)
                return trace_path(child), history

            if child['state'] not in explored and child['state'] not in in_frontier:
                frontier.append(child)
                in_frontier.add(child['state'])

    return [], history


def dls(puzzle, limit, history):
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}
    frontier = [start]

    while frontier:
        node = frontier.pop()
        history.append(node)

        if node['state'] == puzzle['goal']:
            return node

        if node['path_cost'] >= limit:
            continue

        if not is_cycle(node):
            for action in get_moves(node['state']):
                frontier.append(make_move(node, action))
    return None


def ids(puzzle):
    history = []
    for depth in range(100):
        result = dls(puzzle, depth, history)
        if result:
            return trace_path(result), history
    return [], history


def ucs(puzzle):
    goal = puzzle['goal']
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}

    # Tính cost = path_cost (số lần di chuyển) + get_diff (số ô sai vị trí)
    start_cost = start['path_cost'] + get_diff(start['state'], goal)
    step = 0

    frontier = []
    heapq.heappush(frontier, (start_cost, step, start))
    step += 1

    best_path_cost = {start['state']: start['path_cost']}
    explored = set()
    history = []

    while frontier:
        current_cost, _, node = heapq.heappop(frontier)
        state = node['state']
        history.append(node)

        if state in explored: continue
        if state == goal: return trace_path(node), history

        explored.add(state)

        for action in get_moves(state):
            child = make_move(node, action)
            child_state = child['state']
            child_path_cost = child['path_cost']
            cost = child_path_cost + get_diff(child_state, goal)

            if child_state not in explored:
                if child_state not in best_path_cost or child_path_cost < best_path_cost[child_state]:
                    heapq.heappush(frontier, (cost, step, child))
                    best_path_cost[child_state] = child_path_cost
                    step += 1

    return [], history


def greedy(puzzle):
    goal = puzzle['goal']
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}

    h_start = manhattan(start['state'], goal)
    step = 0

    frontier = []
    heapq.heappush(frontier, (h_start, step, start))
    in_frontier = {start['state']}

    reached = set()
    history = []

    while frontier:
        _, _, n = heapq.heappop(frontier)
        in_frontier.remove(n['state'])
        history.append(n)

        if n['state'] == goal:
            return trace_path(n), history

        reached.add(n['state'])

        for action in get_moves(n['state']):
            m = make_move(n, action)

            if m['state'] not in in_frontier and m['state'] not in reached:
                h_m = manhattan(m['state'], goal)
                heapq.heappush(frontier, (h_m, step, m))
                in_frontier.add(m['state'])
                step += 1

    return [], history


def a_star(puzzle):
    goal = puzzle['goal']
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}

    g_start = manhattan(start['state'], goal) + start['path_cost']
    h_start = inversions(start['state'])
    f_start = g_start + h_start

    step = 0
    frontier = []
    heapq.heappush(frontier, (f_start, step, start))
    step += 1

    best_g_cost = {start['state']: g_start}
    explored = set()
    history = []

    while frontier:
        f_cost, _, node = heapq.heappop(frontier)
        state = node['state']
        history.append(node)

        if state in explored: continue
        if state == goal: return trace_path(node), history

        explored.add(state)

        for action in get_moves(state):
            child = make_move(node, action)
            child_state = child['state']

            g_child = manhattan(child_state, goal) + child['path_cost']
            h_child = inversions(child_state)
            f_child = g_child + h_child

            if child_state not in explored:
                if child_state not in best_g_cost or g_child < best_g_cost[child_state]:
                    heapq.heappush(frontier, (f_child, step, child))
                    best_g_cost[child_state] = g_child
                    step += 1

    return [], history


def ida_dls(puzzle, limit, history):
    goal = puzzle['goal']
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}
    frontier = [start]

    while frontier:
        node = frontier.pop()
        history.append(node)

        if node['state'] == goal:
            return node

        g_node = manhattan(node['state'], goal) + node['path_cost']
        h_node = inversions(node['state'])
        f_node = g_node + h_node

        if f_node > limit:
            continue
        if not is_cycle(node):
            for action in get_moves(node['state']):
                frontier.append(make_move(node, action))
    return None


def ida_star(puzzle):
    goal = puzzle['goal']
    start_state = puzzle['init']
    h_start = inversions(start_state)
    g_start = manhattan(start_state, goal) + 0
    limit = g_start + h_start

    history = []
    for _ in range(100):
        result = ida_dls(puzzle, limit, history)
        if result:
            return trace_path(result), history
        limit += h_start

    return [], history


def simple_hill_climbing(puzzle):
    goal = puzzle['goal']
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}

    current = start
    history = [current]

    while True:
        if current['state'] == goal:
            return trace_path(current), history
        current_h = manhattan(current['state'], goal)
        found_better = False

        for action in get_moves(current['state']):
            neighbor = make_move(current, action)
            neighbor_h = manhattan(neighbor['state'], goal)

            if neighbor_h < current_h:
                current = neighbor
                history.append(current)
                found_better = True
                break

        if not found_better:
            break

    return [], history


def steepest_ascent_hill_climbing(puzzle):
    goal = puzzle['goal']
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}

    current = start
    history = [current]

    while True:
        if current['state'] == goal:
            return trace_path(current), history

        current_h = manhattan(current['state'], goal)

        best_neighbor = None
        best_h = current_h

        for action in get_moves(current['state']):
            neighbor = make_move(current, action)
            neighbor_h = manhattan(neighbor['state'], goal)

            if neighbor_h < best_h:
                best_h = neighbor_h
                best_neighbor = neighbor

        if best_neighbor is not None:
            current = best_neighbor
            history.append(current)
        else:
            break

    return [], history


def stochastic_hill_climbing(puzzle):
    goal = puzzle['goal']
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}

    current = start
    history = [current]

    while True:
        if current['state'] == goal:
            return trace_path(current), history

        current_h = manhattan(current['state'], goal)
        better_neighbors = []

        # Sinh tất cả trạng thái lân cận và lọc ra tập Better_Neighbors
        for action in get_moves(current['state']):
            neighbor = make_move(current, action)
            neighbor_h = manhattan(neighbor['state'], goal)

            if neighbor_h < current_h:
                better_neighbors.append(neighbor)

        if not better_neighbors:
            break

        current = random.choice(better_neighbors)
        history.append(current)

    return [], history


def random_restart_hill_climbing(puzzle):
    goal = puzzle['goal']
    start_state = puzzle['init']

    MAX_RESTART = 5
    history = []

    for i in range(MAX_RESTART):
        current = {'state': start_state, 'parent': None, 'action': None, 'path_cost': 0}
        history.append(current)

        while True:
            if current['state'] == goal:
                return trace_path(current), history

            current_h = manhattan(current['state'], goal)
            better_neighbors = []

            for action in get_moves(current['state']):
                neighbor = make_move(current, action)
                neighbor_h = manhattan(neighbor['state'], goal)

                if neighbor_h < current_h:
                    better_neighbors.append(neighbor)

            if not better_neighbors:
                break

            current = random.choice(better_neighbors)
            history.append(current)

    return [], history


def local_beam_search(puzzle, k=2):
    goal = puzzle['goal']
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}

    current_state_set = [start]
    history = [start]

    while True:
        neighbor_states = []

        for state_node in current_state_set:
            for action in get_moves(state_node['state']):
                neighbor = make_move(state_node, action)
                neighbor_states.append(neighbor)

        if not neighbor_states:
            break

        for neighbor in neighbor_states:
            if neighbor['state'] == goal:
                history.append(neighbor)
                return trace_path(neighbor), history

        neighbor_states.sort(key=lambda n: manhattan(n['state'], goal))
        next_state_set = []
        seen_in_beam = set()

        for n in neighbor_states:
            if n['state'] not in seen_in_beam:
                seen_in_beam.add(n['state'])
                next_state_set.append(n)
            if len(next_state_set) == k:
                break

        current_states_tuple = set(node['state'] for node in current_state_set)
        next_states_tuple = set(node['state'] for node in next_state_set)
        if current_states_tuple == next_states_tuple:
            break

        current_state_set = next_state_set
        for node in current_state_set:
            history.append(node)

    return [], history

# ==========================================
# 3. GIAO DIỆN & MÔ PHỎNG
# ==========================================
def draw_board(state, is_goal=False):
    color = "lightgreen" if is_goal else "white"
    for i, val in enumerate(state):
        tiles[i].config(text=str(val) if val else "", bg=color if val else "gray")


def simulate(history, path, idx=0):
    if idx < len(history):
        node = history[idx]
        is_goal = (node['state'] == puzzle['goal'])

        draw_board(node['state'], is_goal=is_goal)

        action = node['action'] if node['action'] else "0"

        algo = current_algo.get()
        state = node['state']
        goal = puzzle['goal']

        if algo in ["BFS", "DFS", "IDS"]:
            cost_str = f"{node['path_cost']}"

        elif algo == "UCS":
            cost_val = node['path_cost'] + get_diff(state, goal)
            cost_str = f"{cost_val}"

        elif algo in ["Greedy", "Simple Hill Climbing", "Steepest Ascent Hill Climbing",
                      "Stochastic Hill Climbing", "Random Restart Hill Climbing", "Local Beam Search"]:
            h_val = manhattan(state, goal)
            cost_str = f"{h_val}"

        elif algo in ["A*", "IDA*"]:
            g_val = manhattan(state, goal) + node['path_cost']
            h_val = inversions(state)
            f_val = g_val + h_val
            cost_str = f"{f_val}"

        else:
            cost_str = str(node['path_cost'])

        log_box.insert(tk.END, f"Bước {idx + 1}: {node['state']} ({action}, {cost_str})\n")
        log_box.see(tk.END)

        root.after(1000, simulate, history, path, idx + 1)
    else:
        if path:
            log_box.insert(tk.END, "\n--- ĐÃ TÌM THẤY ĐÍCH! ---\n")
            log_box.see(tk.END)
            moves = [n['action'] for n in path if n['action']]
            path_str = " - ".join(moves) if moves else "Đã đến đích!"
            result_label.config(text=f"Các bước thực hiện:\n{path_str}")
        else:
            log_box.insert(tk.END, "\n--- Thuật toán bị mắc kẹt ---\n")
            log_box.see(tk.END)
            result_label.config(text="Không tìm thấy đường tới đích!")

        start_btn.config(text="Bắt đầu", state="normal")
        start_btn.config(text="Bắt đầu", state="normal")

def run_algo():
    start_btn.config(text="...", state="disabled")
    log_box.delete(1.0, tk.END)
    result_label.config(text="...")
    root.update()

    algo = current_algo.get()
    if algo == "BFS":
        path, history = bfs(puzzle)
    elif algo == "DFS":
        path, history = dfs(puzzle)
    elif algo == "IDS":
        path, history = ids(puzzle)
    elif algo == "UCS":
        path, history = ucs(puzzle)
    elif algo == "Greedy":
        path, history = greedy(puzzle)
    elif algo == "A*":
        path, history = a_star(puzzle)
    elif algo == "IDA*":
        path, history = ida_star(puzzle)
    elif algo == "Simple Hill Climbing":
        path, history = simple_hill_climbing(puzzle)
    elif algo == "Steepest Ascent Hill Climbing":
        path, history = steepest_ascent_hill_climbing(puzzle)
    elif algo == "Stochastic Hill Climbing":
        path, history = stochastic_hill_climbing(puzzle)
    elif algo == "Random Restart Hill Climbing":
        path, history = random_restart_hill_climbing(puzzle)
    elif algo == "Local Beam Search":
        path, history = local_beam_search(puzzle, k=2)

    if history:
        log_box.insert(tk.END, f"[{algo}]\nĐã duyệt: {len(history)} trạng thái\n\n")
        simulate(history, path, 0)
    else:
        log_box.insert(tk.END, "Vô nghiệm!\n")
        result_label.config(text="Không có trạng thái nào được duyệt!")
        start_btn.config(text="Bắt đầu", state="normal")

def toggle_menu():
    if menu.winfo_x() < 0:
        menu.place(x=0, y=0)
        menu_btn.config(text="✕")
    else:
        menu.place(x=-300, y=0)
        menu_btn.config(text="☰")


def set_algo(name):
    current_algo.set(name)
    status_label.config(text=f"Thuật toán: {name}")
    start_btn.config(text="Bắt đầu", state="normal")
    log_box.delete(1.0, tk.END)
    result_label.config(text="")
    draw_board(puzzle['init'])
    toggle_menu()


# ==========================================
# KHỞI TẠO TKINTER
# ==========================================
root = tk.Tk()
root.title("8-PUZZLE")
root.geometry("750x550")
root.config(bg="lightgray")

current_algo = tk.StringVar(value="BFS")

top_bar = tk.Frame(root, bg="black", height=40)
top_bar.pack(fill="x")
top_bar.pack_propagate(False)

menu_btn = tk.Button(top_bar, text="☰", font=("Arial", 14, "bold"), fg="white", bg="black", bd=0, command=toggle_menu)
menu_btn.pack(side="left", padx=10)

status_label = tk.Label(top_bar, text="Thuật toán: BFS", font=("Arial", 11, "bold"), fg="white", bg="black")
status_label.pack(side="right", padx=15)

main_frame = tk.Frame(root, bg="lightgray")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

left_frame = tk.Frame(main_frame, bg="lightgray", width=300)
left_frame.pack(side="left", fill="y", padx=10)

board = tk.Frame(left_frame, bg="black")
board.pack(pady=20)

tiles = []
for i in range(9):
    lbl = tk.Label(board, font=("Arial", 32, "bold"), width=3, height=1)
    lbl.grid(row=i // 3, column=i % 3, padx=1, pady=1)
    tiles.append(lbl)

start_btn = tk.Button(left_frame, text="Bắt đầu", font=("Arial", 14, "bold"), bg="green", fg="white", bd=0, padx=20,
                      pady=5, command=run_algo)
start_btn.pack(pady=10)

right_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
right_frame.pack(side="right", fill="both", expand=True)

tk.Label(right_frame, text="LOGS", font=("Arial", 10, "bold"), bg="lightgray").pack(fill="x")

scroll = tk.Scrollbar(right_frame)
scroll.pack(side="right", fill="y")

log_box = tk.Text(right_frame, font=("Courier", 10), yscrollcommand=scroll.set, bg="white")
log_box.pack(side="left", fill="both", expand=True, padx=5, pady=5)
scroll.config(command=log_box.yview)

bottom_frame = tk.Frame(root, bg="white", height=80)
bottom_frame.pack(fill="x", side="bottom")
bottom_frame.pack_propagate(False)

result_label = tk.Label(bottom_frame, text="", font=("Arial", 12, "bold"), fg="black", bg="white")
result_label.pack(expand=True)

menu = tk.Frame(root, bg="black", width=300, height=550)
menu.place(x=-300, y=0)
menu.pack_propagate(False)

tk.Label(menu, text="THUẬT TOÁN", font=("Arial", 10, "bold"), fg="gray", bg="black", pady=15).pack(fill="x")
menu_canvas = tk.Canvas(menu, bg="black", highlightthickness=0)
menu_scrollbar = tk.Scrollbar(menu, orient="vertical", command=menu_canvas.yview)
scrollable_frame = tk.Frame(menu_canvas, bg="black")
scrollable_frame.bind(
    "<Configure>",
    lambda e: menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
)

menu_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=280)
menu_canvas.configure(yscrollcommand=menu_scrollbar.set)

menu_canvas.pack(side="left", fill="both", expand=True)
menu_scrollbar.pack(side="right", fill="y")

for name in ["BFS", "DFS", "IDS", "UCS", "Greedy", "A*", "IDA*", "Simple Hill Climbing", "Steepest Ascent Hill Climbing",
             "Stochastic Hill Climbing", "Random Restart Hill Climbing", "Local Beam Search"]:
    tk.Button(scrollable_frame, text=name, font=("Arial", 12, "bold"), fg="white", bg="black", bd=0, anchor="w", padx=20, pady=10,
              command=lambda n=name: set_algo(n)).pack(fill="x")

def _on_mousewheel(event):
    if menu.winfo_x() >= 0:
        menu_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
root.bind_all("<MouseWheel>", _on_mousewheel)

puzzle = {
    'init': (2, 8, 3, 1, 6, 4, 7, 0, 5),
    'goal': (1, 2, 3, 8, 0, 4, 7, 6, 5)
}

draw_board(puzzle['init'])
root.mainloop()