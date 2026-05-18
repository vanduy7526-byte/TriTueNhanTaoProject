""""DFS 8-PUZZLE"""
import tkinter as tk

def get_child(node, act):
    state = list(node['state'])
    idx = state.index(0)
    r, c = idx // 3, idx % 3

    if act == 'U': dr, dc = -1, 0
    elif act == 'D': dr, dc = 1, 0
    elif act == 'L': dr, dc = 0, -1
    elif act == 'R': dr, dc = 0, 1

    new_idx = (r + dr) * 3 + (c + dc)
    state[idx], state[new_idx] = state[new_idx], state[idx]

    return {'state': tuple(state), 'parent': node}

def get_acts(state):
    acts = []
    idx = state.index(0)
    r, c = idx // 3, idx % 3
    if r > 0: acts.append('U')
    if r < 2: acts.append('D')
    if c > 0: acts.append('L')
    if c < 2: acts.append('R')
    return acts

def get_path(node):
    path = []
    while node:
        path.append(node['state'])
        node = node['parent']
    return path[::-1]

def dfs(prob):
    node = {'state': prob['init'], 'parent': None}
    if node['state'] == prob['goal']: return get_path(node)

    q = [node]
    vis = set()

    while q:
        node = q.pop()
        vis.add(node['state'])

        for act in get_acts(node['state']):
            child = get_child(node, act)

            in_q = any(n['state'] == child['state'] for n in q)
            if child['state'] not in vis and not in_q:
                if child['state'] == prob['goal']:
                    return get_path(child)
                q.append(child)
    return []

def draw(state):
    for i, val in enumerate(state):
        cells[i].config(text=str(val) if val else "", bg="white" if val else "gray")

def animate(path, step=0):
    if step < len(path):
        draw(path[step])
        root.after(800, animate, path, step + 1)
    else:
        btn.config(text="Đã hoàn thành!")

def start():
    root.update()
    path = dfs(prob)
    if path:
        animate(path)

root = tk.Tk()
root.title("DFS 8-PUZZLE")
root.geometry("300x380")

board_frame = tk.Frame(root, bg="black")
board_frame.pack(pady=20)

cells = []

for i in range(9):
    lbl = tk.Label(
        board_frame,
        font=("Arial", 36, "bold"),
        width=3,
        height=1,
    )

    lbl.grid(row=i//3, column=i%3, padx=1, pady=1)
    cells.append(lbl)

btn = tk.Button(
    root,
    text="Bắt đầu",
    font=("Arial", 14, "bold"),
    command=start
)

btn.pack(pady=10)

prob = {
    'init': (2, 8, 3, 1, 6, 4, 7, 0, 5),
    'goal': (1, 2, 3, 8, 0, 4, 7, 6, 5)
}

draw(prob['init'])

root.mainloop()