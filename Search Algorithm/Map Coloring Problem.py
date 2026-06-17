import tkinter as tk
import copy
import random

# 1. DỮ LIỆU BÀI TOÁN
variables = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T']
domains = {var: ['red', 'blue', 'green'] for var in variables}

neighbors = {
    'WA': ['NT', 'SA'],
    'NT': ['WA', 'SA', 'Q'],
    'SA': ['WA', 'NT', 'Q', 'NSW', 'V'],
    'Q': ['NT', 'SA', 'NSW'],
    'NSW': ['Q', 'SA', 'V'],
    'V': ['SA', 'NSW'],
    'T': []
}

vn_colors = {'red': 'Đỏ', 'blue': 'Xanh', 'green': 'Lục'}
step_counter = 1
current_domains = {}

# 1. Lấy danh sách tất cả các cặp kề nhau
edges = set()
for u in variables:
    for v in neighbors[u]:
        edge = tuple(sorted((u, v)))
        edges.add(edge)


# 2. CÁC HÀM TIỆN ÍCH CHUNG
def format_assignment(assignment):
    items = [f"{k}={vn_colors[v]}" for k, v in assignment.items()]
    return ", ".join(items)


def format_domain(dom_list):
    return ", ".join([vn_colors[c] for c in dom_list])


def check_consistency(var, value, assignment):
    for neighbor in neighbors[var]:
        if neighbor in assignment and assignment[neighbor] == value:
            return False, neighbor
    return True, None



# 3. CÁC THUẬT TOÁN

def select_unassigned_variable_basic(assignment):
    for var in variables:
        if var not in assignment: return var


def solve_csp_basic():
    global step_counter
    step_counter = 1
    yield {}, f"=== CHẠY THUẬT TOÁN BACKTRACKING ===\nB{step_counter}: Khởi tạo\n- Assignment = {{}}\n" + "-" * 30
    yield from recursive_backtracking({})


def recursive_backtracking(assignment):
    global step_counter
    if len(assignment) == len(variables):
        yield assignment.copy(), "=> HOÀN THÀNH THUẬT TOÁN"
        return True
    var = select_unassigned_variable_basic(assignment)
    step_counter += 1
    yield assignment.copy(), f"B{step_counter}: Chọn biến {var}"
    first_try = True
    for value in domains[var]:
        color_vn = vn_colors[value]
        action_msg = f"- Gán giá trị cho {var} = {color_vn}" if first_try else f"- Thử giá trị khác: {var} = {color_vn}"
        first_try = False
        is_valid, conflict_var = check_consistency(var, value, assignment)
        if is_valid:
            yield assignment.copy(), f"{action_msg}\n- Kiểm tra ràng buộc => Thỏa"
            assignment[var] = value
            yield assignment.copy(), f"- Assignment = {{{format_assignment(assignment)}}}\n" + "-" * 30
            if (yield from recursive_backtracking(assignment)): return True
            del assignment[var]
            yield assignment.copy(), f"- QUAY LUI: Xóa gán {var} = {color_vn}"
        else:
            yield assignment.copy(), f"{action_msg}\n- Kiểm tra ràng buộc => Vi phạm (do {var} kề {conflict_var})"
    return False


def select_unassigned_variable_mrv(assignment):
    unassigned = [v for v in variables if v not in assignment]
    unassigned.sort(key=lambda x: (len(current_domains[x]), variables.index(x)))
    return unassigned[0]


def solve_csp_fc():
    global step_counter, current_domains
    step_counter = 1
    current_domains = copy.deepcopy(domains)
    yield {}, f"=== CHẠY THUẬT TOÁN FORWARD CHECKING ===\nB{step_counter}: Khởi tạo\n- Assignment = {{}}\n" + "-" * 30
    yield from forward_checking_search({})


def forward_checking_search(assignment):
    global step_counter
    if len(assignment) == len(variables):
        yield assignment.copy(), "=> HOÀN THÀNH THUẬT TOÁN"
        return True
    var = select_unassigned_variable_mrv(assignment)
    step_counter += 1
    for value in list(current_domains[var]):
        color_vn = vn_colors[value]
        yield assignment.copy(), f"B{step_counter}: Chọn {var} = {color_vn} -> Thỏa"
        assignment[var] = value
        yield assignment.copy(), f"- Assignment = {{{format_assignment(assignment)}}}"
        removed_items = []
        for neighbor in neighbors[var]:
            if neighbor not in assignment:
                if value in current_domains[neighbor]:
                    current_domains[neighbor].remove(value)
                    removed_items.append((neighbor, value))
        unassigned_neighbors = [n for n in neighbors[var] if n not in assignment]
        vars_to_log = unassigned_neighbors if unassigned_neighbors else [n for n in variables if n not in assignment]
        fc_parts = [f"D({n}) = {{{format_domain(current_domains[n])}}}" for n in vars_to_log if n in current_domains]
        fc_log = "- Forward checking: " + ", ".join(fc_parts) if fc_parts else "- Forward checking: Không có tác động"
        empty_domain_var = next((n for n in variables if n not in assignment and len(current_domains[n]) == 0), None)
        if empty_domain_var:
            yield assignment.copy(), f"{fc_log}\n[!] LỖI FC: D({empty_domain_var}) bị rỗng!"
            for n, val in removed_items: current_domains[n].append(val)
            del assignment[var]
            yield assignment.copy(), f"- QUAY LUI: Xóa gán {var} = {color_vn}, phục hồi miền giá trị\n" + "-" * 30
        else:
            yield assignment.copy(), f"{fc_log}\n" + "-" * 30
            if (yield from forward_checking_search(assignment)): return True
            for n, val in removed_items: current_domains[n].append(val)
            del assignment[var]
            yield assignment.copy(), f"- QUAY LUI TỪ DƯỚI LÊN: Xóa gán {var} = {color_vn}, phục hồi miền giá trị\n" + "-" * 30
    return False


def ac3_log_style(queue, assignment):
    global current_domains
    removed_history = []
    if not queue: return True, removed_history
    q_str = "{" + ", ".join([f"{u} {v}" for u, v in queue]) + "}"
    log_msg = f"  B1: Q = {q_str}"
    yield assignment.copy(), log_msg
    step_ac3 = 2
    while queue:
        xi, xj = queue.pop(0)
        domain_xi_before = list(current_domains[xi])
        domain_xj = [assignment[xj]] if xj in assignment else current_domains[xj]
        log_xet = f"  B{step_ac3}: Xét {xi} {xj}:\n"
        step_ac3 += 1
        removed_vals = []
        for x_val in domain_xi_before:
            color_x = vn_colors[x_val]
            supporting_y = [y_val for y_val in domain_xj if x_val != y_val]
            if supporting_y:
                y_str = " v ".join([vn_colors[y] for y in supporting_y])
                log_xet += f"    • {xi}={color_x} -> tồn tại {xj}={y_str} => thỏa\n"
            else:
                log_xet += f"    • {xi}={color_x} -> KHÔNG tồn tại {xj} => Loại {color_x} khỏi D({xi})\n"
                current_domains[xi].remove(x_val)
                removed_history.append((xi, x_val))
                removed_vals.append(x_val)
        if removed_vals:
            if len(current_domains[xi]) == 0:
                yield assignment.copy(), log_xet + f"    => [!] Ngõ cụt: D({xi}) rỗng!"
                return False, removed_history
            for xk in neighbors[xi]:
                if xk != xj and xk not in assignment:
                    if (xk, xi) not in queue:
                        queue.append((xk, xi))
        q_str = "{" + ", ".join([f"{u} {v}" for u, v in queue]) + "}"
        log_xet += f"  Q = {q_str}"
        yield assignment.copy(), log_xet
    return True, removed_history


def ac3_search():
    global current_domains
    current_domains = copy.deepcopy(domains)
    assignment = {}
    yield assignment.copy(), f"=== CHẠY THUẬT TOÁN AC-3 ===\n- Khởi tạo miền giá trị đầy đủ cho tất cả các vùng."
    queue = []
    for u in variables:
        for v in neighbors[u]:
            queue.append((u, v))
    is_safe, removed_history = yield from ac3_log_style(queue, assignment)
    yield assignment.copy(), "\n=> HOÀN THÀNH THUẬT TOÁN AC-3."

def count_current_conflicts(assignment):
    total = 0
    conflicted_vars = set()
    checks_str = []
    conflict_desc = []

    for u, v in edges:
        c_u = assignment[u]
        c_v = assignment[v]
        if c_u == c_v:
            checks_str.append(f"{u} ≠ {v} -> vi phạm ({vn_colors[c_u]}={vn_colors[c_v]})")
            conflict_desc.append(f"{u} và {v}")
            total += 1
            conflicted_vars.add(u)
            conflicted_vars.add(v)
        else:
            checks_str.append(f"{u} ≠ {v} -> thỏa mãn")

    return total, conflicted_vars, checks_str, conflict_desc


def solve_csp_min_conflicts(max_steps=50):
    # Bước 1: Khởi tạo ngẫu nhiên
    assignment = {var: random.choice(domains[var]) for var in variables}

    assign_str = format_assignment(assignment)
    log_msg = f"=== CHẠY THUẬT TOÁN MIN-CONFLICTS ===\nBước 1. Khởi tạo lời giải ban đầu \nGiả sử ta gán ban đầu: {assign_str}.\nKiểm tra ràng buộc:\n"

    total, conf_vars, checks_str, conf_desc = count_current_conflicts(assignment)
    log_msg += "; ".join(checks_str) + "\n"

    if total > 0:
        log_msg += f"Có {total} xung đột giữa " + ", ".join(conf_desc) + ".\n" + "-" * 30
    else:
        log_msg += "Không có xung đột nào. Hoàn thành thuật toán\n" + "-" * 30
        yield assignment.copy(), log_msg
        return True

    yield assignment.copy(), log_msg

    # Lặp lại sửa lỗi
    step_idx = 2
    for i in range(max_steps):
        if total == 0:
            yield assignment.copy(), "\n=> HOÀN THÀNH THUẬT TOÁN!"
            return True

        # Bước 2: Chọn biến gây xung đột
        var = random.choice(list(conf_vars))
        log_msg = f"Bước {step_idx}. Chọn một biến gây xung đột\nChọn ngẫu nhiên một biến trong cặp xung đột. Giả sử chọn {var}.\n"
        log_msg += f"Tìm giá trị làm giảm xung đột bằng cách thử tất cả các giá trị trong miền của {var}:\n"

        min_c = float('inf')
        best_vals = []

        for val in domains[var]:
            c_count = 0
            c_list = []
            for neighbor in neighbors[var]:
                if assignment[neighbor] == val:
                    c_count += 1
                    c_list.append(neighbor)

            color_vn = vn_colors[val]
            if c_count == 0:
                log_msg += f"  {var}={color_vn} -> không xung đột\n"
            else:
                log_msg += f"  {var}={color_vn} -> xung đột với {', '.join(c_list)}\n"

            if c_count < min_c:
                min_c = c_count
                best_vals = [val]
            elif c_count == min_c:
                best_vals.append(val)

        # Chọn ngẫu nhiên nếu có nhiều màu có cùng số xung đột tối thiểu
        best_val = random.choice(best_vals)
        assignment[var] = best_val

        log_msg += f"Như vậy, giá trị tốt nhất để gán cho biến {var} là {vn_colors[best_val]}."

        # Bước 3: Cập nhật
        step_idx += 1
        assign_str = format_assignment(assignment)
        log_update = f"Bước {step_idx}. Cập nhật lời giải\nGán lại: {assign_str}.\n"

        # Tính lại xung đột
        total, conf_vars, checks_str, conf_desc = count_current_conflicts(assignment)
        log_update += f"Số xung đột hiện tại: {total}\n" + "-" * 30

        yield assignment.copy(), log_msg + "\n\n" + log_update
        step_idx += 1

    yield assignment.copy(), f"=> ĐẠT GIỚI HẠN {max_steps} BƯỚC MÀ CHƯA TÌM RA LỜI GIẢI HOÀN HẢO."
    return False

# 4. GIAO DIỆN & TƯƠNG TÁC
nodes_coords = {
    'WA': (100, 150), 'NT': (250, 100), 'SA': (250, 220),
    'Q': (400, 120), 'NSW': (400, 240), 'V': (350, 320), 'T': (350, 420)
}
node_objects = {}
is_auto_playing = False
solver_generator = None


def draw_graph():
    for u in variables:
        for v in neighbors[u]:
            x1, y1 = nodes_coords[u]
            x2, y2 = nodes_coords[v]
            canvas.create_line(x1, y1, x2, y2, width=2, fill="gray")
    for node in variables:
        x, y = nodes_coords[node]
        circle = canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill="white", outline="black", width=2)
        canvas.create_text(x, y, text=node, font=("Arial", 10, "bold"))
        node_objects[node] = circle


def clear_log():
    log_text.config(state=tk.NORMAL)
    log_text.delete('1.0', tk.END)
    log_text.config(state=tk.DISABLED)


def write_log(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)
    log_text.config(state=tk.DISABLED)


def update_colors(assignment):
    color_map = {'red': '#ff6b6b', 'green': '#51cf66', 'blue': '#339af0'}
    for node in variables:
        current_color = assignment.get(node, None)
        fill_color = color_map.get(current_color, "white")
        canvas.itemconfig(node_objects[node], fill=fill_color)


def reset_simulation(*args):
    global solver_generator, is_auto_playing
    is_auto_playing = False
    btn_auto.config(text="Tự động chạy", state=tk.NORMAL)
    btn_next.config(state=tk.NORMAL)
    update_colors({})
    clear_log()
    selected_algo = algo_var.get()

    if selected_algo == "Backtracking":
        solver_generator = solve_csp_basic()
    elif selected_algo == "Forward Checking":
        solver_generator = solve_csp_fc()
    elif selected_algo == "Min-Conflicts":
        solver_generator = solve_csp_min_conflicts()
    else:
        solver_generator = ac3_search()


def next_step():
    global is_auto_playing
    try:
        assignment, log_msg = next(solver_generator)
        update_colors(assignment)
        write_log(log_msg)
    except StopIteration:
        write_log("--- KẾT THÚC ---")
        is_auto_playing = False
        btn_auto.config(text="Tự động chạy", state=tk.DISABLED)
        btn_next.config(state=tk.DISABLED)


def toggle_auto():
    global is_auto_playing
    is_auto_playing = not is_auto_playing
    if is_auto_playing:
        btn_auto.config(text="Dừng tự động")
        btn_next.config(state=tk.DISABLED)
        auto_step()
    else:
        btn_auto.config(text="Tự động chạy")
        btn_next.config(state=tk.NORMAL)


def auto_step():
    if is_auto_playing:
        next_step()
        root.after(400, auto_step)

# 5. KHỞI CHẠY CHƯƠNG TRÌNH

if __name__ == "__main__":
    root = tk.Tk()
    root.title("TÔ MÀU BẢN ĐỒ")

    canvas_frame = tk.Frame(root)
    canvas_frame.pack(side=tk.LEFT, padx=10, pady=10)
    canvas = tk.Canvas(canvas_frame, width=500, height=500, bg="white")
    canvas.pack()

    controls_frame = tk.Frame(canvas_frame)
    controls_frame.pack(pady=10)

    algo_var = tk.StringVar(root)
    algo_var.set("Backtracking")

    algo_menu = tk.OptionMenu(controls_frame, algo_var, "Backtracking", "Forward Checking", "AC-3",
                              "Min-Conflicts",
                              command=reset_simulation)
    algo_menu.config(font=("Arial", 10))
    algo_menu.pack(side=tk.TOP, pady=5, fill=tk.X)

    btn_frame = tk.Frame(controls_frame)
    btn_frame.pack(side=tk.TOP)
    btn_next = tk.Button(btn_frame, text="Bước tiếp", command=next_step, font=("Arial", 10))
    btn_next.pack(side=tk.LEFT, padx=5)
    btn_auto = tk.Button(btn_frame, text="Tự động chạy", command=toggle_auto, font=("Arial", 10))
    btn_auto.pack(side=tk.LEFT, padx=5)
    btn_reset = tk.Button(btn_frame, text="Làm mới", command=reset_simulation, font=("Arial", 10), bg="#ffc9c9")
    btn_reset.pack(side=tk.LEFT, padx=5)

    log_frame = tk.Frame(root)
    log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    tk.Label(log_frame, text="Các bước thực hiên:", font=("Arial", 12, "bold")).pack(anchor="w")
    log_text = tk.Text(log_frame, width=70, height=30, font=("Consolas", 10), state=tk.DISABLED)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.config(yscrollcommand=scrollbar.set)

    draw_graph()
    reset_simulation()

    root.mainloop()