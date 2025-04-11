import flet as ft
import copy

ROWS, COLS = 8, 8
EMPTY = 0
PLAYER = 1
AI = 2
KING_PLAYER = 3
KING_AI = 4
DEPTH = 4

def initial_board():
    board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    for row in range(3):
        for col in range(COLS):
            if (row + col) % 2 == 1:
                board[row][col] = AI
    for row in range(5, 8):
        for col in range(COLS):
            if (row + col) % 2 == 1:
                board[row][col] = PLAYER
    return board

def is_inside(x, y):
    return 0 <= x < ROWS and 0 <= y < COLS

def get_moves(board, x, y):
    piece = board[x][y]
    directions = []
    if piece in (PLAYER, KING_PLAYER):
        directions += [(-1, -1), (-1, 1)]
    if piece in (AI, KING_AI):
        directions += [(1, -1), (1, 1)]
    if piece in (KING_PLAYER, KING_AI):
        directions += [(-d[0], -d[1]) for d in directions]

    moves, captures = [], []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if is_inside(nx, ny):
            if board[nx][ny] == EMPTY:
                moves.append((nx, ny))
            elif board[nx][ny] != piece and board[nx][ny] != EMPTY:
                jump_x, jump_y = nx + dx, ny + dy
                if is_inside(jump_x, jump_y) and board[jump_x][jump_y] == EMPTY:
                    captures.append((jump_x, jump_y, nx, ny))
    return captures if captures else moves

def get_all_moves(board, player):
    moves = []
    for x in range(ROWS):
        for y in range(COLS):
            if board[x][y] in ([PLAYER, KING_PLAYER] if player == PLAYER else [AI, KING_AI]):
                for move in get_moves(board, x, y):
                    moves.append(((x, y), move))
    return moves

def move_piece(board, from_pos, to_pos):
    x1, y1 = from_pos
    x2, y2 = to_pos[0], to_pos[1]
    piece = board[x1][y1]
    board[x1][y1] = EMPTY
    board[x2][y2] = piece
    captured = False
    if len(to_pos) == 4:
        cap_x, cap_y = to_pos[2], to_pos[3]
        board[cap_x][cap_y] = EMPTY
        captured = True
    if piece == PLAYER and x2 == 0:
        board[x2][y2] = KING_PLAYER
    elif piece == AI and x2 == ROWS - 1:
        board[x2][y2] = KING_AI
    return captured

def evaluate(board):
    score = 0
    for row in board:
        for cell in row:
            if cell == PLAYER:
                score += 1
            elif cell == AI:
                score -= 1
            elif cell == KING_PLAYER:
                score += 2
            elif cell == KING_AI:
                score -= 2
    return score

def minimax(board, depth, maximizing, alpha, beta):
    if depth == 0 or not get_all_moves(board, PLAYER) or not get_all_moves(board, AI):
        return evaluate(board), None
    best_move = None
    if maximizing:
        max_eval = float("-inf")
        for move in get_all_moves(board, AI):
            new_board = copy.deepcopy(board)
            move_piece(new_board, move[0], move[1])
            eval, _ = minimax(new_board, depth - 1, False, alpha, beta)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float("inf")
        for move in get_all_moves(board, PLAYER):
            new_board = copy.deepcopy(board)
            move_piece(new_board, move[0], move[1])
            eval, _ = minimax(new_board, depth - 1, True, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def main(page: ft.Page):
    page.title = "Jogo de Damas"
    page.bgcolor = "#7B3F00"  # cor madeira
    page.padding = 30

    board = initial_board()
    buttons = [[None for _ in range(COLS)] for _ in range(ROWS)]
    current = PLAYER
    selected = None
    score_player, score_ai = 0, 0
    stats = {"vitorias": 0, "derrotas": 0, "empates": 0}

    score_text = ft.Text(f"Peças comidas - Você: {score_player} | IA: {score_ai}")
    result_text = ft.Text("Vitórias: 0 | Derrotas: 0 | Empates: 0")

    def render():
        for x in range(ROWS):
            for y in range(COLS):
                piece = board[x][y]
                color = "#006400" if (x + y) % 2 == 0 else "#000000"
                shape = ""
                if piece == PLAYER:
                    shape = "🔴"
                elif piece == AI:
                    shape = "⚪"
                elif piece == KING_PLAYER:
                    shape = "🔴♛"
                elif piece == KING_AI:
                    shape = "⚪♕"
                buttons[x][y].text = shape
                buttons[x][y].style = ft.ButtonStyle(bgcolor=color)
        score_text.value = f"Peças comidas - Você: {score_player} | IA: {score_ai}"
        result_text.value = f"Vitórias: {stats['vitorias']} | Derrotas: {stats['derrotas']} | Empates: {stats['empates']}"
        page.update()

    def reset_game(e=None):
        nonlocal board, current, selected, score_player, score_ai
        board = initial_board()
        current = PLAYER
        selected = None
        score_player = 0
        score_ai = 0
        render()

    def check_game_over():
        nonlocal stats
        player_moves = get_all_moves(board, PLAYER)
        ai_moves = get_all_moves(board, AI)
        if not player_moves and not ai_moves:
            stats["empates"] += 1
            return True
        elif not player_moves:
            stats["derrotas"] += 1
            return True
        elif not ai_moves:
            stats["vitorias"] += 1
            return True
        return False

    def on_click(x, y):
        nonlocal selected, current, score_player
        if current != PLAYER:
            return
        if selected:
            moves = get_moves(board, *selected)
            for m in moves:
                if (x, y) == (m[0], m[1]):
                    captured = move_piece(board, selected, m)
                    if captured:
                        score_player += 1
                    selected = None
                    current = AI
                    render()
                    if check_game_over():
                        render()
                        return
                    page.run_task(ai_move)
                    return
            selected = None
        if board[x][y] in [PLAYER, KING_PLAYER]:
            selected = (x, y)

    async def ai_move():
        nonlocal current, score_ai
        _, best = minimax(board, DEPTH, True, float("-inf"), float("inf"))
        if best:
            captured = move_piece(board, best[0], best[1])
            if captured:
                score_ai += 1
        if check_game_over():
            render()
            return
        current = PLAYER
        render()

    grid = ft.Column(spacing=0)
    for x in range(ROWS):
        row = ft.Row(spacing=0)
        for y in range(COLS):
            b = ft.TextButton("", width=50, height=50,
                            style=ft.ButtonStyle(
                                shape=ft.BoxShape.CIRCLE,
                                bgcolor="#000000"
                            ),
                            on_click=lambda e, x=x, y=y: on_click(x, y))
            buttons[x][y] = b
            row.controls.append(b)
        grid.controls.append(row)

    page.add(
        ft.Column([
            ft.Row([score_text, ft.ElevatedButton("Resetar Jogo", on_click=reset_game)], alignment="spaceBetween"),
            grid,
            result_text,
        ], spacing=20)
    )
    render()

ft.app(target=main)