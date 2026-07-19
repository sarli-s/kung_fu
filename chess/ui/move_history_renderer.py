import cv2
import numpy as np
from chess.ui.config import CELL_SIZE


class MoveHistoryRenderer:
    """Renders move history panels on left and right sides of the board."""
    
    def __init__(self, asset_loader, panel_width=150, row_height=40):
        self.asset_loader = asset_loader
        self.panel_width = panel_width
        self.row_height = row_height
        self.white_panel_rows = []  # Cached rendered rows for white
        self.black_panel_rows = []  # Cached rendered rows for black
    
    def render_move_row(self, move):
        """Render a single move row. Returns numpy array (BGR)."""
        row_img = np.ones((self.row_height, self.panel_width, 3), dtype=np.uint8) * 240  # Light gray bg
        
        # Red background if capture
        if move["is_capture"]:
            row_img[:] = (100, 100, 200)  # Light red (BGR)
        
        # Get piece sprite (small)
        sprite = self.asset_loader.get_piece_sprite(move["piece"], state="idle", sprite_idx=0)
        if sprite is not None:
            # Resize sprite to fit in row (small icon)
            h, w = sprite.shape[:2]
            icon_size = self.row_height - 4
            scale = icon_size / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            sprite_small = cv2.resize(sprite, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            # Place sprite on left side of row
            y_offset = (self.row_height - new_h) // 2
            x_offset = 4
            if sprite_small.shape[2] == 4:  # RGBA
                alpha = sprite_small[:, :, 3] / 255.0
                for c in range(3):
                    row_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w, c] = \
                        (1 - alpha) * row_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w, c] + \
                        alpha * sprite_small[:, :, c]
            else:
                row_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = sprite_small
        
        # Add text: "From→To #N" using chess notation
        text = f"{move['from_notation']}→{move['to_notation']} #{move['move_num']}"
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.35
        thickness = 1
        text_color = (0, 0, 0) if not move["is_capture"] else (255, 255, 255)
        
        cv2.putText(row_img, text, (40, 25), font, font_scale, text_color, thickness)
        
        return row_img
    
    def render_panel(self, move_tracker, player, board_height):
        """Render moves panel for given player. Returns numpy array."""
        is_white = player == "white"
        panel_rows = self.white_panel_rows if is_white else self.black_panel_rows
        new_moves = move_tracker.get_new_moves(player)
        
        # Add new rows to cache (incremental)
        for move in new_moves:
            row_img = self.render_move_row(move)
            panel_rows.append(row_img)
        
        # Stack all rows vertically
        if not panel_rows:
            return np.ones((board_height, self.panel_width, 3), dtype=np.uint8) * 220
        
        total_height = len(panel_rows) * self.row_height
        if total_height > board_height:
            # Show only last N rows that fit
            visible_rows = panel_rows[-(board_height // self.row_height):]
        else:
            visible_rows = panel_rows
        
        panel_img = np.vstack(visible_rows) if visible_rows else np.ones((board_height, self.panel_width, 3), dtype=np.uint8) * 220
        
        # Pad to board height if needed
        if panel_img.shape[0] < board_height:
            padding = np.ones((board_height - panel_img.shape[0], self.panel_width, 3), dtype=np.uint8) * 220
            panel_img = np.vstack([padding, panel_img])
        elif panel_img.shape[0] > board_height:
            panel_img = panel_img[-board_height:, :]
        
        return panel_img
    
    def clear(self):
        """Clear cached rows."""
        self.white_panel_rows = []
        self.black_panel_rows = []
