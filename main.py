#Repo URL 
#https://github.com/sarli-s/kung_fu

import sys
from play.core.parser import parse_input, parse_board
from play.core.commands import handle_commands

def main(parser=parse_board, handler=handle_commands):
    text = sys.stdin.read()
    board_lines, command_lines = parse_input(text)
    board, error = parser(board_lines)
    if error:
        print(error)
        return
    handler(board, command_lines)

if __name__ == "__main__":
    main()
