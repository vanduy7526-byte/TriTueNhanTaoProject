import random


def P_moves(x, y, visited):
    valid_dirs = []
    if x < 3: valid_dirs.append(("D", x + 1, y))
    if x > 0: valid_dirs.append(("U", x - 1, y))
    if y < 3: valid_dirs.append(("R", x, y + 1))
    if y > 0: valid_dirs.append(("L", x, y - 1))

    unvisited = [d[0] for d in valid_dirs if (d[1], d[2]) not in visited]
    if unvisited:
        return unvisited
    else:
        return [d[0] for d in valid_dirs]


def rules(x, y, state, visited):
    if state == 1:
        state = 0
        moves = P_moves(x, y, visited)
        action = random.choice(moves)
    else:
        moves = P_moves(x, y, visited)
        action = random.choice(moves)
    return action, state


def print_grid(grid, x, y, step):
    print(f"So buoc: {step}")
    for i in range(4):
        row = ""
        for j in range(4):
            if i == x and j == y:
                row += f"[{grid[i][j]}] "
            else:
                row += f" {grid[i][j]}  "
        print(row)  # Đã sửa lề để in đủ 4 hàng
    print()


grid = [[random.choice([0, 1]) for _ in range(4)] for _ in range(4)]
x, y = random.randint(0, 3), random.randint(0, 3)
step, max_steps = 0, 50

# BỘ NHỚ (Internal State)
visited = []

while any(1 in row for row in grid) and step < max_steps:
    if (x, y) not in visited:
        visited.append((x, y))

    action, new_state = rules(x, y, grid[x][y], visited)
    grid[x][y] = new_state

    if action == "U":
        x -= 1
    elif action == "D":
        x += 1
    elif action == "L":
        y -= 1
    elif action == "R":
        y += 1

    step += 1
    print_grid(grid, x, y, step)

if any(1 in row for row in grid):
    print("Chua sach")
else:
    print("Da don sach")