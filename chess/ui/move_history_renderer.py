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
    
    def _render_captured_strip(self, moves, is_white):
        icon_size = 24
        padding = 4
        bg = (230, 230, 230) if is_white else (50, 50, 50)

        captured_tokens = [
            m["captured_piece"] for m in moves
            if m.get("is_capture") and m.get("captured_piece")
        ]
        if not captured_tokens:
            return None

        icons_per_row = max(1, (self.panel_width - padding) // (icon_size + 2))
        num_rows = (len(captured_tokens) + icons_per_row - 1) // icons_per_row
        row_h = icon_size + padding * 2
        strip = np.ones((row_h * num_rows, self.panel_width, 3), dtype=np.uint8)
        strip[:] = bg

        for i, token in enumerate(captured_tokens):
            row_idx = i // icons_per_row
            col_idx = i % icons_per_row
            x = padding + col_idx * (icon_size + 2)
            y = row_idx * row_h + padding
            sprite = self.asset_loader.get_piece_sprite(token, state="idle", sprite_idx=0)
            if sprite is None:
                continue
            h, w = sprite.shape[:2]
            scale = icon_size / max(w, h)
            sw, sh = int(w * scale), int(h * scale)
            sprite_small = cv2.resize(sprite, (sw, sh), interpolation=cv2.INTER_AREA)
            yo = y + (icon_size - sh) // 2
            xo = x + (icon_size - sw) // 2
            if sprite_small.shape[2] == 4:
                alpha = sprite_small[:, :, 3] / 255.0
                for c in range(3):
                    strip[yo:yo+sh, xo:xo+sw, c] = (
                        (1 - alpha) * strip[yo:yo+sh, xo:xo+sw, c] +
                        alpha * sprite_small[:, :, c]
                    )
            else:
                strip[yo:yo+sh, xo:xo+sw] = sprite_small

        return strip

    def render_panel(self, move_tracker, player, board_height, username=None, score=0, elapsed_ms=0):
        is_white = player == "white"
        panel_rows = self.white_panel_rows if is_white else self.black_panel_rows
        new_moves = move_tracker.get_new_moves(player)

        for move in new_moves:
            row_img = self.render_move_row(move)
            panel_rows.append(row_img)

        # --- header ---
        header_h = 90
        header = np.zeros((header_h, self.panel_width, 3), dtype=np.uint8)

        bg     = (240, 240, 240) if is_white else (40, 40, 40)
        accent = (200, 200, 200) if is_white else (70, 70, 70)
        fg     = (30,  30,  30)  if is_white else (220, 220, 220)
        header[:] = bg

        # top accent stripe
        header[:6, :] = accent

        # color circle
        dot_fill   = (255, 255, 255) if is_white else (15, 15, 15)
        dot_border = (160, 160, 160) if is_white else (120, 120, 120)
        cv2.circle(header, (18, 28), 11, dot_fill,   -1, cv2.LINE_AA)
        cv2.circle(header, (18, 28), 11, dot_border,  1, cv2.LINE_AA)

        # username — large
        label = (username or player.capitalize())[:14]
        cv2.putText(header, label, (36, 34),
                    cv2.FONT_HERSHEY_DUPLEX, 0.55, fg, 1, cv2.LINE_AA)

        # color badge
        badge_text = "White" if is_white else "Black"
        badge_bg   = (180, 180, 180) if is_white else (80, 80, 80)
        badge_fg   = (50,  50,  50)  if is_white else (200, 200, 200)
        (bw, bh), _ = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_SIMPLEX, 0.32, 1)
        bx, by = 8, 52
        cv2.rectangle(header, (bx - 3, by - bh - 2), (bx + bw + 3, by + 3), badge_bg, -1, cv2.LINE_AA)
        cv2.putText(header, badge_text, (bx, by),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, badge_fg, 1, cv2.LINE_AA)

        # score
        cv2.putText(header, f"Score: {score}", (8, 76),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, fg, 1, cv2.LINE_AA)

        # timer (right-aligned)
        total_s    = int(elapsed_ms / 1000)
        timer_text = f"{total_s // 60:02d}:{total_s % 60:02d}"
        (tw, _), _ = cv2.getTextSize(timer_text, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
        cv2.putText(header, timer_text, (self.panel_width - tw - 8, 76),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, fg, 1, cv2.LINE_AA)

        captured_strip = self._render_captured_strip(move_tracker.get_moves(player), is_white)
        header_total = np.vstack([header, captured_strip]) if captured_strip is not None else header
        content_height = board_height - header_total.shape[0]
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

        return np.vstack([header_total, body])
    
    def clear(self):
        self.white_panel_rows = []
        self.black_panel_rows = []
