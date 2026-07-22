import cv2
from chess.services.board_builder import build_board
from chess.ui.renderer import BoardRenderer
from chess.ui.display import DisplayLoop

def run_gui():
    # Create a simple starting position (white at bottom, black at top)
    board_lines = [
        "bR bN bB bQ bK bB bN bR",  # row 0 (top)
        "bP bP bP bP bP bP bP bP",  # row 1
        ". . . . . . . .",          # row 2
        ". . . . . . . .",          # row 3
        ". . . . . . . .",          # row 4
        ". . . . . . . .",          # row 5
        "wP wP wP wP wP wP wP wP",  # row 6
        "wR wN wB wK wQ wB wN wR",  # row 7 (bottom)
    ]
    
    player_names = {"white": "White", "black": "Black"}

    engine = build_board(board_lines)
    renderer = BoardRenderer()
    display_loop = DisplayLoop(engine, renderer, player_names=player_names)
    display_loop.run()
