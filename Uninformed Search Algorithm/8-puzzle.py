import tkinter as tk
from collections import deque
import heapq

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


def heuristic(state, goal):
    return sum(1 for i in range(9) if state[i] != 0 and state[i] != goal[i])


def is_cycle(node):
    curr = node['parent']
    while curr:
        if curr['state'] == node['state']: return True
        curr = curr['parent']
    return False


# ==========================================
# CÁC THUẬT TOÁN
# ==========================================
def bfs(puzzle):
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}
    history = []

    if start['state'] == puzzle['goal']:
        history.append(start)
        return trace_path(start), history

    queue = deque([start])
    in_queue = {start['state']}
    visited = set()

    while queue:
        node = queue.popleft()
        in_queue.remove(node['state'])
        visited.add(node['state'])
        history.append(node)

        for action in get_moves(node['state']):
            child = make_move(node, action)

            if child['state'] == puzzle['goal']:
                history.append(child)
                return trace_path(child), history

            if child['state'] not in visited and child['state'] not in in_queue:
                queue.append(child)
                in_queue.add(child['state'])
    return [], history


def dfs(puzzle):
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}
    history = []

    if start['state'] == puzzle['goal']:
        history.append(start)
        return trace_path(start), history

    stack = [start]
    in_stack = {start['state']}
    visited = set()

    while stack:
        node = stack.pop()
        in_stack.remove(node['state'])
        visited.add(node['state'])
        history.append(node)

        for action in get_moves(node['state']):
            child = make_move(node, action)

            if child['state'] == puzzle['goal']:
                history.append(child)
                return trace_path(child), history

            if child['state'] not in visited and child['state'] not in in_stack:
                stack.append(child)
                in_stack.add(child['state'])
    return [], history


def dls(puzzle, limit, history):
    start = {'state': puzzle['init'], 'parent': None, 'action': None, 'path_cost': 0}
    stack = [start]

    while stack:
        node = stack.pop()
        history.append(node)

        if node['state'] == puzzle['goal']:
            return node

        if node['path_cost'] >= limit:
            continue

        if not is_cycle(node):
            for action in get_moves(node['state']):
                stack.append(make_move(node, action))
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

    init_total_cost = start['path_cost'] + heuristic(start['state'], goal)
    step = 0

    frontier = []
    heapq.heappush(frontier, (init_total_cost, step, start))
    step += 1

    best_path_cost = {start['state']: start['path_cost']}
    visited = set()
    history = []

    while frontier:
        total_cost, _, node = heapq.heappop(frontier)
        state = node['state']
        history.append(node)

        if state in visited: continue
        if state == goal: return trace_path(node), history

        visited.add(state)

        for action in get_moves(state):
            child = make_move(node, action)
            next_state = child['state']
            next_path_cost = child['path_cost']
            next_total_cost = next_path_cost + heuristic(next_state, goal)

            if next_state not in visited:
                if next_state not in best_path_cost or next_path_cost < best_path_cost[next_state]:
                    heapq.heappush(frontier, (next_total_cost, step, child))
                    step += 1
                    best_path_cost[next_state] = next_path_cost

    return [], history


# ==========================================
# GIAO DIỆN & MÔ PHỎNG
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
        cost = node['path_cost']
        log_box.insert(tk.END, f"Bước {idx + 1}: {node['state']} ({action},{cost})\n")
        log_box.see(tk.END)

        root.after(50, simulate, history, path, idx + 1)
    else:
        log_box.insert(tk.END, "\n--- ĐÃ TÌM THẤY ĐÍCH! ---\n")
        log_box.see(tk.END)

        if path:
            moves = [n['action'] for n in path if n['action']]
            path_str = " - ".join(moves) if moves else "Đã đến đích!"
            result_label.config(text=f"Các bước thực hiện:\n{path_str}")

        start_btn.config(text="Hoàn thành!", state="normal")


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

    if path:
        log_box.insert(tk.END, f"[{algo}]\nĐã duyệt: {len(history)} trạng thái\n\n")
        simulate(history, path, 0)
    else:
        log_box.insert(tk.END, "Vô nghiệm!\n")
        result_label.config(text="Không tìm thấy đường!")
        start_btn.config(text="Bắt đầu", state="normal")


def toggle_menu():
    if menu.winfo_x() < 0:
        menu.place(x=0, y=0)
        menu_btn.config(text="✕")
    else:
        menu.place(x=-160, y=0)
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

# Khung Trên
top_bar = tk.Frame(root, bg="black", height=40)
top_bar.pack(fill="x")
top_bar.pack_propagate(False)

menu_btn = tk.Button(
    top_bar,
    text="☰",
    font=("Arial", 14, "bold"),
    fg="white",
    bg="black",
    bd=0,
    command=toggle_menu
)
menu_btn.pack(side="left", padx=10)

status_label = tk.Label(
    top_bar,
    text="Thuật toán: BFS",
    font=("Arial", 11, "bold"),
    fg="white",
    bg="black"
)
status_label.pack(side="right", padx=15)

# Khung Chính
main_frame = tk.Frame(root, bg="lightgray")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Khung Trái
left_frame = tk.Frame(main_frame, bg="lightgray", width=300)
left_frame.pack(side="left", fill="y", padx=10)

board = tk.Frame(left_frame, bg="black")
board.pack(pady=20)

tiles = []
for i in range(9):
    lbl = tk.Label(board, font=("Arial", 32, "bold"), width=3, height=1)
    lbl.grid(row=i // 3, column=i % 3, padx=1, pady=1)
    tiles.append(lbl)

start_btn = tk.Button(
    left_frame,
    text="Bắt đầu",
    font=("Arial", 14, "bold"),
    bg="green",
    fg="white",
    bd=0,
    padx=20,
    pady=5,
    command=run_algo
)
start_btn.pack(pady=10)

# Khung Phải
right_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
right_frame.pack(side="right", fill="both", expand=True)

tk.Label(
    right_frame,
    text="LOGS",
    font=("Arial", 10, "bold"),
    bg="lightgray"
).pack(fill="x")

scroll = tk.Scrollbar(right_frame)
scroll.pack(side="right", fill="y")

log_box = tk.Text(
    right_frame,
    font=("Courier", 10),
    yscrollcommand=scroll.set,
    bg="white"
)
log_box.pack(side="left", fill="both", expand=True, padx=5, pady=5)

scroll.config(command=log_box.yview)

# Khung Dưới
bottom_frame = tk.Frame(root, bg="white", height=80)
bottom_frame.pack(fill="x", side="bottom")
bottom_frame.pack_propagate(False)

result_label = tk.Label(
    bottom_frame,
    text="",
    font=("Arial", 12, "bold"),
    fg="black",
    bg="white"
)
result_label.pack(expand=True)

# Khung Menu
menu = tk.Frame(root, bg="black", width=160, height=550)
menu.place(x=-160, y=0)

tk.Label(
    menu,
    text="THUẬT TOÁN",
    font=("Arial", 10, "bold"),
    fg="gray",
    bg="black",
    pady=15
).pack(fill="x")

for name in ["BFS", "DFS", "IDS", "UCS"]:
    tk.Button(
        menu,
        text=name,
        font=("Arial", 12, "bold"),
        fg="white",
        bg="black",
        bd=0,
        anchor="w",
        padx=20,
        pady=10,
        command=lambda n=name: set_algo(n)
    ).pack(fill="x")

puzzle = {
    'init': (2, 8, 3, 1, 6, 4, 7, 0, 5),
    'goal': (1, 2, 3, 8, 0, 4, 7, 6, 5)
}

draw_board(puzzle['init'])

root.mainloop()