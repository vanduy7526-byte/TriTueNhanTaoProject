import tkinter as tk

def get_child(node, act):
    state = list(node['state'])
    idx = state.index(0)
    r, c = idx // 3, idx % 3

    if act == 'U':
        dr, dc = -1, 0
    elif act == 'D':
        dr, dc = 1, 0
    elif act == 'L':
        dr, dc = 0, -1
    elif act == 'R':
        dr, dc = 0, 1

    new_idx = (r + dr) * 3 + (c + dc)
    state[idx], state[new_idx] = state[new_idx], state[idx]

    return {
        'state': tuple(state),
        'parent': node,
        'action': act,
        'path_cost': node['path_cost'] + 1
    }


def get_acts(state):
    acts = []
    idx = state.index(0)
    r, c = idx // 3, idx % 3
    if c > 0: acts.append('L')
    if c < 2: acts.append('R')
    if r > 0: acts.append('U')
    if r < 2: acts.append('D')
    return acts


def get_path(node):
    path = []
    while node:
        path.append(node['state'])
        node = node['parent']
    return path[::-1]


def is_cycle(node):
    curr = node['parent']
    while curr:
        if curr['state'] == node['state']:
            return True
        curr = curr['parent']
    return False


def dls(prob, l):
    node = {
        'state': prob['init'],
        'parent': None,
        'action': None,
        'path_cost': 0
    }
    frontier = [node]
    result = "failure"

    while frontier:
        node = frontier.pop()

        if node['state'] == prob['goal']:
            return node
        if node['path_cost'] >= l:
            result = "cutoff"
        elif not is_cycle(node):
            for act in get_acts(node['state']):
                child = get_child(node, act)
                frontier.append(child)
    return result


def ids(prob):
    depth = 0
    while True:
        result = dls(prob, depth)
        if result != "cutoff":
            return result
        depth += 1

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
    btn.config(state="disabled")
    root.update()
    result_node = ids(prob)
    if result_node != "failure":
        path = get_path(result_node)
        animate(path)
    else:
        btn.config(text="Vô nghiệm!")


root = tk.Tk()
root.title("IDS 8-PUZZLE")
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

    lbl.grid(row=i // 3, column=i % 3, padx=1, pady=1)
    cells.append(lbl)

btn = tk.Button(
    root,
    text="Bắt đầu",
    font=("Arial", 14, "bold"),
    command=start
)

btn.pack(pady=10)
prob = {
    'init': (1, 2, 3, 4, 0, 6, 7, 5, 8),
    'goal': (1, 2, 3, 4, 5, 6, 7, 8, 0)
}
draw(prob['init'])

root.mainloop()