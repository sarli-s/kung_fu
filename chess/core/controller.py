from chess.view.board_printer import print_board
from chess.config import ChessConfig


def _pixel_to_cell(engine, x, y, config=None, border_x=0, border_y=0):
    cell_size = (config or ChessConfig).cell_size
    x_adjusted = x - border_x
    y_adjusted = y - border_y
    col, row = x_adjusted // cell_size, y_adjusted // cell_size
    if 0 <= row < engine.rows() and 0 <= col < engine.cols():
        return row, col
    return None


def _handle_print(engine, cmd, ctx):
    print_board(engine)


def _handle_wait(engine, cmd, ctx):
    ms = int(cmd.split()[1])
    engine.advance(ms)
    ctx["selected"] = None


def _handle_jump(engine, cmd, ctx):
    parts = cmd.split()
    x, y = int(parts[1]), int(parts[2])
    cell = _pixel_to_cell(engine, x, y)
    if cell is not None:
        engine.request_jump(cell[0], cell[1])


def _try_select(engine, row, col, ctx):
    if not engine.is_moving(row, col):
        ctx["selected"] = (row, col)


def _try_move(engine, row, col, ctx):
    selected = ctx["selected"]
    if selected is not None:
        engine.request_move(selected[0], selected[1], row, col)
        ctx["selected"] = None


def _handle_click(engine, cmd, ctx):
    if ctx["game_over"]:
        return
    parts = cmd.split()
    x, y = int(parts[1]), int(parts[2])
    cell = _pixel_to_cell(engine, x, y)
    if cell is None:
        return
    row, col = cell
    selected = ctx["selected"]
    if not engine.is_empty(row, col):
        if selected is not None and engine.same_color(selected[0], selected[1], row, col):
            _try_select(engine, row, col, ctx)
        elif selected is None:
            _try_select(engine, row, col, ctx)
        else:
            _try_move(engine, row, col, ctx)
    else:
        _try_move(engine, row, col, ctx)


COMMAND_HANDLERS = {
    "print board": _handle_print,
    "wait":        _handle_wait,
    "jump":        _handle_jump,
    "click":       _handle_click,
}


def handle_commands(engine, commands, handlers=COMMAND_HANDLERS, ctx=None):
    if ctx is None:
        ctx = {"selected": None, "game_over": False}
        engine.subscribe("on_game_over", lambda **_: ctx.update({"game_over": True}))
    for cmd in commands:
        key = next((k for k in handlers if cmd == k or cmd.startswith(k + " ")), None)
        if key:
            handlers[key](engine, cmd, ctx)
    return ctx
