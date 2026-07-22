import cv2
import numpy as np
from chess.ui.config import BOARD_ROWS, BOARD_COLS, CELL_SIZE, BOARD_BORDER_X, BOARD_BORDER_Y
from chess.ui.assets import AssetLoader
from chess.ui.animator import Animator
from chess.ui.state_manager import get_piece_state
from chess.ui.motion import get_smooth_position
from chess.ui.img import Img
from chess.ui.move_history_renderer import MoveHistoryRenderer


class BoardRenderer:
    def __init__(self):
        self.asset_loader = AssetLoader()
        self.animator = Animator()
        self.board_bg = self.asset_loader.get_board_background()
        self.move_history_renderer = MoveHistoryRenderer(self.asset_loader)

    def render(self, engine, selected_cell=None, delta_ms=0, player_names=None, scores=None, elapsed_ms=0):
        player_names = player_names or {}
        scores = scores or {}
        board_canvas = self.board_bg.copy()
        board_canvas_img = Img(board_canvas)

        if selected_cell is not None:
            row, col = selected_cell
            x = col * CELL_SIZE + BOARD_BORDER_X
            y = row * CELL_SIZE + BOARD_BORDER_Y
            square_img = self.asset_loader.get_square_image()
            if square_img is not None:
                Img(square_img).draw_on(board_canvas_img, x, y, exact_pixel=True)

        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                token = engine.cell(row, col)
                if token == ".":
                    continue

                state = get_piece_state(engine, row, col)
                frame_idx = self.animator.get_frame_index(row, col, token, state, delta_ms)
                sprite = self.asset_loader.get_piece_sprite(token, state=state, sprite_idx=frame_idx)
                if sprite is None:
                    continue

                smooth_row, smooth_col = get_smooth_position(engine, row, col)
                x = smooth_col * CELL_SIZE
                y = smooth_row * CELL_SIZE

                Img(sprite).draw_on(board_canvas_img, x, y, exact_pixel=False, cell_size=CELL_SIZE, board_border_x=BOARD_BORDER_X, board_border_y=BOARD_BORDER_Y)

        board_height = board_canvas.shape[0]

        if board_canvas.shape[2] == 4:  # np.hstack requires matching channel counts; alpha must be stripped first
            board_canvas = cv2.cvtColor(board_canvas, cv2.COLOR_BGRA2BGR)

        white_panel = self.move_history_renderer.render_panel(engine.move_tracker, "white", board_height, username=player_names.get("white"), score=scores.get("white", 0), elapsed_ms=elapsed_ms)
        black_panel = self.move_history_renderer.render_panel(engine.move_tracker, "black", board_height, username=player_names.get("black"), score=scores.get("black", 0), elapsed_ms=elapsed_ms)

        canvas = np.hstack([white_panel, board_canvas, black_panel])

        return canvas
