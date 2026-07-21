import cv2
import numpy as np
from pathlib import Path
from chess.ui.config import PIECES_DIR, DEFAULT_PIECE_STATE, DEFAULT_SPRITE_INDEX, CELL_SIZE, SQUARE_IMAGE, BOARD_IMAGE
from chess.ui.errors import AssetLoadError


class AssetLoader:
    def __init__(self):
        self._sprite_cache = {}
        self._square_image = None
        self._board_bg = None

    def get_board_background(self):
        if self._board_bg is not None:
            return self._board_bg

        path_str = str(BOARD_IMAGE)
        # cv2.imread silently fails on Unicode paths; open+imdecode is the workaround.
        with open(path_str, 'rb') as f:
            img_data = np.frombuffer(f.read(), np.uint8)
        img = cv2.imdecode(img_data, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise AssetLoadError(f"Board image not found or failed to decode: {BOARD_IMAGE}")
        
        self._board_bg = img
        return img

    def get_piece_sprite(self, token, state=DEFAULT_PIECE_STATE, sprite_idx=DEFAULT_SPRITE_INDEX):
        cache_key = (token, state, sprite_idx)
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]

        piece_dir = PIECES_DIR / token / "states" / state / "sprites"
        sprite_path = piece_dir / f"{sprite_idx + 1}.png"

        if not sprite_path.exists():
            return None

        with open(str(sprite_path), 'rb') as f:
            img_data = np.frombuffer(f.read(), np.uint8)
        img = cv2.imdecode(img_data, cv2.IMREAD_UNCHANGED)
        if img is None:
            return None

        h, w = img.shape[:2]
        scale = min(CELL_SIZE / w, CELL_SIZE / h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        self._sprite_cache[cache_key] = img
        return img

    def get_square_image(self):
        if self._square_image is not None:
            return self._square_image

        # cv2.imread silently fails on Unicode paths; open+imdecode is the workaround.
        with open(str(SQUARE_IMAGE), 'rb') as f:
            img_data = np.frombuffer(f.read(), np.uint8)
        img = cv2.imdecode(img_data, cv2.IMREAD_UNCHANGED)
        if img is None:
            return None

        img = cv2.resize(img, (CELL_SIZE, CELL_SIZE), interpolation=cv2.INTER_AREA)
        self._square_image = img
        return img

    def clear_cache(self):
        self._sprite_cache.clear()
        self._square_image = None
        self._board_bg = None
