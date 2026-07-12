import sys
from chess.services.input_parser import parse_input
from chess.services.board_builder import build_board
from chess.core.controller import handle_commands
from chess.utils.errors import ChessError

def main(parser=build_board, handler=handle_commands):
    text = sys.stdin.read()
    board_lines, command_lines = parse_input(text)
    try:
        board = parser(board_lines)
    except ChessError as e:
        print(e)
        return
    handler(board, command_lines)

if __name__ == "__main__":
    main()
