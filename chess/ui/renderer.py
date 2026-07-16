import cv2
import numpy as np
from chess.ui.config import BOARD_ROWS, BOARD_COLS, CELL_SIZE, BOARD_BORDER_X, BOARD_BORDER_Y
from chess.ui.assets import AssetLoader
from chess.ui.animator import Animator
from chess.ui.state_manager import StateManager
from chess.ui.img import Img


class BoardRenderer:
    def __init__(self):
        self.asset_loader = AssetLoader()
        self.animator = Animator()
        self.board_bg = self.asset_loader.get_board_background()

    def _get_smooth_position(self, engine, row, col):
        """Calculate smooth interpolated position for a piece during movement."""
        cmd = engine.get_move_command(row, col)
        if cmd is None:
            return (row, col)
        
        # Get current and target positions
        from_row, from_col = cmd.from_row, cmd.from_col
        to_row, to_col = cmd.current_row, cmd.current_col
        
        # Find progress between checkpoints
        checkpoints = cmd.checkpoints
        if not checkpoints:
            return (to_row, to_col)
        
        # Find which segment we're in
        prev_checkpoint = None
        next_checkpoint = None
        for i, (due_time, r, c) in enumerate(checkpoints):
            if due_time <= cmd.elapsed:
                prev_checkpoint = (due_time, r, c)
            else:
                next_checkpoint = (due_time, r, c)
                break
        
        # If no next checkpoint, return current position
        if next_checkpoint is None:
            return (to_row, to_col)
        
        # If no prev checkpoint, start from origin
        if prev_checkpoint is None:
            prev_time, prev_r, prev_c = 0, from_row, from_col
        else:
            prev_time, prev_r, prev_c = prev_checkpoint
        
        next_time, next_r, next_c = next_checkpoint
        
        # Calculate progress in this segment
        time_in_segment = cmd.elapsed - prev_time
        segment_duration = next_time - prev_time
        
        if segment_duration <= 0:
            return (prev_r, prev_c)
        
        progress = min(1.0, time_in_segment / segment_duration)
        
        # Linear interpolation
        smooth_row = prev_r + (next_r - prev_r) * progress
        smooth_col = prev_c + (next_c - prev_c) * progress
        
        return (smooth_row, smooth_col)

    def render(self, engine, selected_cell=None, delta_ms=0):
        """Render current engine state to canvas. Returns numpy array (BGR/BGRA)."""
        canvas = self.board_bg.copy()
        canvas_img = Img(canvas)

        # Draw selection square if selected
        if selected_cell is not None:
            row, col = selected_cell
            x = col * CELL_SIZE + BOARD_BORDER_X
            y = row * CELL_SIZE + BOARD_BORDER_Y
            square_img = self.asset_loader.get_square_image()
            if square_img is not None:
                Img(square_img).draw_on(canvas_img, x, y, exact_pixel=True)

        # Draw each piece
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                token = engine.cell(row, col)
                if token == ".":  # empty cell
                    continue

                state = StateManager.get_piece_state(engine, row, col)
                frame_idx = self.animator.get_frame_index(row, col, token, state, delta_ms)
                sprite = self.asset_loader.get_piece_sprite(token, state=state, sprite_idx=frame_idx)
                if sprite is None:
                    continue

                # Get smooth interpolated position
                smooth_row, smooth_col = self._get_smooth_position(engine, row, col)
                
                # Calculate pixel position (top-left of cell)
                x = smooth_col * CELL_SIZE
                y = smooth_row * CELL_SIZE

                # Blend sprite onto canvas
                Img(sprite).draw_on(canvas_img, x, y, exact_pixel=False, cell_size=CELL_SIZE, board_border_x=BOARD_BORDER_X, board_border_y=BOARD_BORDER_Y)

        return canvas_img.img

