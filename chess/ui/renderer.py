import cv2
import numpy as np
from chess.ui.config import BOARD_ROWS, BOARD_COLS, CELL_SIZE, BOARD_BORDER_X, BOARD_BORDER_Y
from chess.ui.assets import AssetLoader
from chess.ui.animator import Animator
from chess.ui.state_manager import StateManager


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
        # Copy background
        canvas = self.board_bg.copy()

        # Draw selection square if selected
        if selected_cell is not None:
            row, col = selected_cell
            x = col * CELL_SIZE + BOARD_BORDER_X
            y = row * CELL_SIZE + BOARD_BORDER_Y
            square_img = self.asset_loader.get_square_image()
            if square_img is not None:
                h, w = square_img.shape[:2]
                offset_x = (CELL_SIZE - w) // 2
                offset_y = (CELL_SIZE - h) // 2
                self._blend_sprite_at_pixel(canvas, square_img, x + offset_x, y + offset_y)

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
                self._blend_sprite(canvas, sprite, x, y)

        return canvas

    def _blend_sprite_at_pixel(self, canvas, sprite, x_pos, y_pos):
        """Blend sprite at exact pixel position."""
        h, w = sprite.shape[:2]
        x_pos, y_pos = int(x_pos), int(y_pos)
        
        # Ensure sprite fits
        if y_pos + h > canvas.shape[0] or x_pos + w > canvas.shape[1]:
            return

        roi = canvas[y_pos:y_pos + h, x_pos:x_pos + w]

        # Ensure channel compatibility
        sprite_to_blend = sprite
        if sprite.shape[2] != canvas.shape[2]:
            if sprite.shape[2] == 3 and canvas.shape[2] == 4:
                sprite_to_blend = cv2.cvtColor(sprite, cv2.COLOR_BGR2BGRA)
            elif sprite.shape[2] == 4 and canvas.shape[2] == 3:
                sprite_to_blend = cv2.cvtColor(sprite, cv2.COLOR_BGRA2BGR)

        if sprite_to_blend.shape[2] == 4:  # BGRA
            b, g, r, a = cv2.split(sprite_to_blend)
            mask = a / 255.0
            for c in range(3):
                roi[..., c] = (1 - mask) * roi[..., c] + mask * sprite_to_blend[..., c]
        else:  # BGR
            canvas[y_pos:y_pos + h, x_pos:x_pos + w] = sprite_to_blend

    def _blend_sprite(self, canvas, sprite, x, y):
        """Blend sprite with alpha channel onto canvas at (x, y), centered in cell."""
        h, w = sprite.shape[:2]
        
        # Center sprite in cell
        offset_x = (CELL_SIZE - w) // 2
        offset_y = (CELL_SIZE - h) // 2
        x_pos = int(x + offset_x + BOARD_BORDER_X)
        y_pos = int(y + offset_y + BOARD_BORDER_Y)

        # Ensure sprite fits
        if y_pos + h > canvas.shape[0] or x_pos + w > canvas.shape[1]:
            return

        roi = canvas[y_pos:y_pos + h, x_pos:x_pos + w]

        # Ensure channel compatibility
        sprite_to_blend = sprite
        if sprite.shape[2] != canvas.shape[2]:
            if sprite.shape[2] == 3 and canvas.shape[2] == 4:
                sprite_to_blend = cv2.cvtColor(sprite, cv2.COLOR_BGR2BGRA)
            elif sprite.shape[2] == 4 and canvas.shape[2] == 3:
                sprite_to_blend = cv2.cvtColor(sprite, cv2.COLOR_BGRA2BGR)

        if sprite_to_blend.shape[2] == 4:  # BGRA
            b, g, r, a = cv2.split(sprite_to_blend)
            mask = a / 255.0
            for c in range(3):
                roi[..., c] = (1 - mask) * roi[..., c] + mask * sprite_to_blend[..., c]
        else:  # BGR
            canvas[y_pos:y_pos + h, x_pos:x_pos + w] = sprite_to_blend
