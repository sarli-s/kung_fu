from play.entities.board import Board

VALID_TOKENS = {
    ".", "wK", "bK", "wQ", "bQ", "wR", "bR", "wN", "bN", "wB", "bB", "wP", "bP"
}

def parse_input(text):
    board_lines, command_lines = [], []
    section = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "Board:":
            section = "board"
        elif stripped == "Commands:":
            section = "commands"
        elif section == "board" and stripped:
            board_lines.append(stripped)
        elif section == "commands" and stripped:
            command_lines.append(stripped)
    return board_lines, command_lines

def parse_board(board_lines):
    grid = []
    for line in board_lines:
        row = line.split()
        for token in row:
            if token not in VALID_TOKENS:
                return None, "ERROR UNKNOWN_TOKEN"
        grid.append(row)
    if grid:
        width = len(grid[0])
        for row in grid:
            if len(row) != width:
                return None, "ERROR ROW_WIDTH_MISMATCH"
    return Board(grid), None
