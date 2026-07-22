import cv2
import numpy as np
from chess.ui.config import CELL_SIZE


class MoveHistoryRenderer:
    
    def __init__(self, asset_loader, panel_width=150, row_height=40):
        self.asset_loader = asset_loader
        self.panel_width = panel_width
        self.row_height = row_height
        self.white_panel_rows = []
        self.black_panel_rows = []
    
    def render_move_row(self, move):
        row_img = np.ones((self.row_height, self.panel_width, 3), dtype=np.uint8) * 240
        
        if move["is_capture"]:
            row_img[:] = (100, 100, 200)
        
        sprite = self.asset_loader.get_piece_sprite(move["piece"], state="idle", sprite_idx=0)
        if sprite is not None:
            h, w = sprite.shape[:2]
            icon_size = self.row_height - 4
            scale = icon_size / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            sprite_small = cv2.resize(sprite, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            y_offset = (self.row_height - new_h) // 2
            x_offset = 4
            if sprite_small.shape[2] == 4:
                alpha = sprite_small[:, :, 3] / 255.0
                for c in range(3):
                    row_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w, c] = \
                        (1 - alpha) * row_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w, c] + \
                        alpha * sprite_small[:, :, c]
            else:
                row_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = sprite_small
        
        text = f"{move['from_notation']}→{move['to_notation']} #{move['move_num']}"
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.35
        thickness = 1
        text_color = (0, 0, 0) if not move["is_capture"] else (255, 255, 255)
        
        cv2.putText(row_img, text, (40, 25), font, font_scale, text_color, thickness)
        
        return row_img
    
    def render_panel(self, move_tracker, player, board_height, username=None):
        is_white = player == "white"
        panel_rows = self.white_panel_rows if is_white else self.black_panel_rows
        new_moves = move_tracker.get_new_moves(player)
        
        for move in new_moves:
            row_img = self.render_move_row(move)
            panel_rows.append(row_img)

        # header
        header_h = 50
        header = np.zeros((header_h, self.panel_width, 3), dtype=np.uint8)
        color_bgr = (220, 220, 220) if is_white else (60, 60, 60)
        text_color = (30, 30, 30) if is_white else (220, 220, 220)
        header[:] = color_bgr
        # color dot
        cx, cy = 14, header_h // 2
        dot_color = (255, 255, 255) if is_white else (20, 20, 20)
        cv2.circle(header, (cx, cy), 10, dot_color, -1)
        cv2.circle(header, (cx, cy), 10, (100, 100, 100), 1)
        # name
        label = username or player.capitalize()
        cv2.putText(header, label, (30, cy + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, text_color, 1, cv2.LINE_AA)

        content_height = board_height - header_h
        if not panel_rows:
            body = np.ones((content_height, self.panel_width, 3), dtype=np.uint8) * 220
        else:
            total_height = len(panel_rows) * self.row_height
            if total_height > content_height:
                visible_rows = panel_rows[-(content_height // self.row_height):]
            else:
                visible_rows = panel_rows
            body = np.vstack(visible_rows)
            if body.shape[0] < content_height:
                padding = np.ones((content_height - body.shape[0], self.panel_width, 3), dtype=np.uint8) * 220
                body = np.vstack([padding, body])
            elif body.shape[0] > content_height:
                body = body[-content_height:, :]

        return np.vstack([header, body])
    
    def clear(self):
        self.white_panel_rows = []
        self.black_panel_rows = []
