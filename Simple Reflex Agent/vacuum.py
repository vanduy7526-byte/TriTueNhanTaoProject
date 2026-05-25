import random

def P_moves(x, y):
    moves = []
    if x < 3: moves.append("D")
    if x > 0: moves.append("U")
    if y < 3: moves.append("R")
    if y > 0: moves.append("L")
    return moves

def rules(x, y, state):
    if state == 1:
        state = 0
        moves = P_moves(x, y)
        action = random.choice(moves)
    else:
        moves = P_moves(x, y)
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
        print(row)
    print()

grid = [[random.choice([0, 1]) for _ in range(4)] for _ in range(4)]
x, y = random.randint(0, 3), random.randint(0, 3)
step, max_steps = 0, 50

while any(1 in row for row in grid) and step < max_steps:
    action, new_state = rules(x, y, grid[x][y])
    grid[x][y] = new_state

    if action == "U": x-= 1
    elif action == "D": x += 1
    elif action == "L": y -= 1
    elif action == "R": y += 1
    step += 1
    print_grid(grid, x, y, step)

if any(1 in row for row in grid):
    print("Chua sach")
else:
    print("Da don sach")

