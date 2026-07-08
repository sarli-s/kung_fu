from play.config import ChessConfig

def _pixel_to_cell(board, x, y, config=None):
    cell_size = (config or ChessConfig).cell_size
    col, row = x // cell_size, y // cell_size
    if 0 <= row < board.rows() and 0 <= col < board.cols():
        return row, col
    return None

def _handle_print(board, cmd, ctx):
    print(board)

def _handle_wait(board, cmd, ctx):
    ms = int(cmd.split()[1])
    board.advance(ms)
    ctx["selected"] = None

def _handle_jump(board, cmd, ctx):
    parts = cmd.split()
    x, y = int(parts[1]), int(parts[2])
    cell = _pixel_to_cell(board, x, y)
    if cell is not None:
        board.request_jump(cell[0], cell[1])

def _try_select(board, row, col, ctx):
    if not board.is_moving(row, col):
        ctx["selected"] = (row, col)

def _try_move(board, row, col, ctx):
    selected = ctx["selected"]
    if selected is not None:
        board.request_move(selected[0], selected[1], row, col)
        ctx["selected"] = None

def _handle_click(board, cmd, ctx):
    if ctx["game_over"]:
        return
    parts = cmd.split()
    x, y = int(parts[1]), int(parts[2])
    cell = _pixel_to_cell(board, x, y)
    if cell is None:
        return
    row, col = cell
    selected = ctx["selected"]
    if not board.is_empty(row, col):
        if selected is not None and board.same_color(selected[0], selected[1], row, col):
            _try_select(board, row, col, ctx)
        elif selected is None:
            _try_select(board, row, col, ctx)
        else:
            _try_move(board, row, col, ctx)
    else:
        _try_move(board, row, col, ctx)

COMMAND_HANDLERS = {
    "print board": _handle_print,
    "wait":        _handle_wait,
    "jump":        _handle_jump,
    "click":       _handle_click,
}

def handle_commands(board, commands, handlers=COMMAND_HANDLERS):
    ctx = {"selected": None, "game_over": False}
    board.subscribe("on_game_over", lambda **_: ctx.update({"game_over": True}))
    for cmd in commands:
        key = next((k for k in handlers if cmd == k or cmd.startswith(k + " ")), None)
        if key:
            handlers[key](board, cmd, ctx)
