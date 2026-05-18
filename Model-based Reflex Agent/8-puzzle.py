import random

table = [
    [1, 2, 3],
    [4, 0, 5],
    [7, 8, 6]
]

goal = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

for r in table:
    print(r)
print("------------------")

visited = []
step = 1

while True:
    if table == goal:
        print(f"Thắng trò chơi sau {step - 1} bước.")
        break

    visited.append(str(table))

    for r in range(3):
        for c in range(3):
            if table[r][c] == 0:
                row, col = r, c

    moves = []
    if row > 0: moves.append(("UP", -1, 0))
    if row < 2: moves.append(("DOWN", 1, 0))
    if col > 0: moves.append(("LEFT", 0, -1))
    if col < 2: moves.append(("RIGHT", 0, 1))

    valid_moves = []
    for action, dr, dc in moves:
        table[row][col], table[row + dr][col + dc] = table[row + dr][col + dc], table[row][col]
        if str(table) not in visited:
            valid_moves.append((action, dr, dc))
        table[row][col], table[row + dr][col + dc] = table[row + dr][col + dc], table[row][col]

    if not valid_moves:
        print(f"Không còn đường nào mới để đi.")
        break

    action, dr, dc = random.choice(valid_moves)
    table[row][col], table[row + dr][col + dc] = table[row + dr][col + dc], table[row][col]

    print(f"Bước {step} - Thực hiện: {action}")
    for r in table:
        print(r)
    print("------------------")

    step += 1