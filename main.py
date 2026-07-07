import sys
from play.core.parser import parse_input, parse_board
from play.core.commands import handle_commands

def main():
    text = sys.stdin.read()
    board_lines, command_lines = parse_input(text)
    board, error = parse_board(board_lines)
    if error:
        print(error)
        return
    handle_commands(board, command_lines)

if __name__ == "__main__":
    main()
