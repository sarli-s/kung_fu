CELL_SIZE = 100

def _pixel_to_cell(board, x, y):
    col, row = x // CELL_SIZE, y // CELL_SIZE
    if 0 <= row < board.rows() and 0 <= col < board.cols():
        return row, col
    return None

def handle_commands(board, commands):
    selected = None  # (row, col)
    for cmd in commands:
        if cmd == "print board":
            print(board)
        elif cmd.startswith("wait "):
            ms = int(cmd.split()[1])
            board.advance(ms)
            selected = None
        elif cmd.startswith("click "):
            parts = cmd.split()
            x, y = int(parts[1]), int(parts[2])
            cell = _pixel_to_cell(board, x, y)
            if cell is None:
                continue
            row, col = cell
            piece = board.cell(row, col)
            if piece != ".":
                if selected is not None and board.cell(selected[0], selected[1])[0] == piece[0]:
                    # Friendly piece — replace selection
                    selected = (row, col)
                elif selected is None:
                    # No selection — select this piece
                    selected = (row, col)
                else:
                    # Enemy piece with active selection — capture (move request)
                    board.request_move(selected[0], selected[1], row, col)
                    selected = None
            else:
                if selected is not None:
                    board.request_move(selected[0], selected[1], row, col)
                    selected = None
