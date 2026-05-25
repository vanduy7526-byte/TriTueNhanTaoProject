import random

table = [
    [1, 2, 3],
    [4, 0, 5],
    [7, 8, 6]
]

print("Trạng thái ban đầu:")
for r in table:
    print(r)
print("------------------")

for step in range(1, 10):

    for r in range(3):
        for c in range(3):
            if table[r][c] == 0:
                row, col = r, c

    moves = []
    if row > 0: moves.append(("UP", -1, 0))
    if row < 2: moves.append(("DOWN", 1, 0))
    if col > 0: moves.append(("LEFT", 0, -1))
    if col < 2: moves.append(("RIGHT", 0, 1))

    action, dr, dc = random.choice(moves)
    table[row][col], table[row + dr][col + dc] = table[row + dr][col + dc], table[row][col]

    print(f"Bước {step} - Thực hiện: {action}")
    for r in table:
        print(r)
    print("------------------")