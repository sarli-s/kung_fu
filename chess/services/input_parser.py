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
