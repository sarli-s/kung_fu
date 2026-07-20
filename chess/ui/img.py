import cv2
import numpy as np
from chess.ui.errors import ImageError


class Img:
    def __init__(self, img=None):
        self.img = img

    def put_text(self, txt, x, y, font_size, color=(255, 255, 255), thickness=2):
        if self.img is None:
            raise ImageError("Image not loaded.")
        cv2.putText(self.img, txt, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_size,
                    color, thickness, cv2.LINE_AA)
        return self

    def draw_rectangle(self, x, y, width, height, color=(0, 255, 0), thickness=3):
        if self.img is None:
            raise ImageError("Image not loaded.")
        cv2.rectangle(self.img, (x, y), (x + width, y + height), color, thickness)
        return self

    def draw_on(self, other_img, x, y, exact_pixel=False, cell_size=None, board_border_x=0, board_border_y=0):
        """Args:
            exact_pixel: If True, use exact pixel coords. If False, center in cell.
            cell_size: Required if exact_pixel=False.
        """
        if self.img is None or other_img.img is None:
            raise ImageError("Both images must be loaded before drawing.")

        h, w = self.img.shape[:2]
        H, W = other_img.img.shape[:2]
        
        # Calculate final position
        if exact_pixel:
            x_pos, y_pos = int(x), int(y)
        else:
            if cell_size is None:
                raise ImageError("cell_size required when exact_pixel=False")
            offset_x = (cell_size - w) // 2
            offset_y = (cell_size - h) // 2
            x_pos = int(x + offset_x + board_border_x)
            y_pos = int(y + offset_y + board_border_y)

        if y_pos + h > H or x_pos + w > W:
            return self

        roi = other_img.img[y_pos:y_pos + h, x_pos:x_pos + w]

        # Ensure channel compatibility
        sprite_to_blend = self.img
        if self.img.shape[2] != other_img.img.shape[2]:
            if self.img.shape[2] == 3 and other_img.img.shape[2] == 4:
                sprite_to_blend = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
            elif self.img.shape[2] == 4 and other_img.img.shape[2] == 3:
                sprite_to_blend = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)

        if sprite_to_blend.shape[2] == 4:  # BGRA with alpha
            b, g, r, a = cv2.split(sprite_to_blend)
            mask = a / 255.0
            for c in range(3):
                roi[..., c] = (1 - mask) * roi[..., c] + mask * sprite_to_blend[..., c]
        else:  # BGR
            other_img.img[y_pos:y_pos + h, x_pos:x_pos + w] = sprite_to_blend
        return self

    def show(self, window_name="Image"):
        if self.img is None:
            raise ImageError("Image not loaded.")
        cv2.imshow(window_name, self.img)
        return self
