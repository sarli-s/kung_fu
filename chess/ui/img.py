import cv2
import numpy as np


class Img:
    def __init__(self, img=None):
        self.img = img

    def put_text(self, txt, x, y, font_size, color=(255, 255, 255), thickness=2):
        """Draw text on the image at position (x, y)."""
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.putText(self.img, txt, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_size,
                    color, thickness, cv2.LINE_AA)
        return self

    def draw_rectangle(self, x, y, width, height, color=(0, 255, 0), thickness=3):
        """Draw a rectangle border on the image."""
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.rectangle(self.img, (x, y), (x + width, y + height), color, thickness)
        return self

    def fill_rectangle(self, x, y, width, height, color=(0, 255, 0), alpha=0.5):
        """Fill a rectangle with semi-transparent color."""
        if self.img is None:
            raise ValueError("Image not loaded.")
        overlay = self.img.copy()
        cv2.rectangle(overlay, (x, y), (x + width, y + height), color, -1)
        cv2.addWeighted(overlay, alpha, self.img, 1 - alpha, 0, self.img)
        return self

    def draw_on(self, other_img, x, y):
        """Blend this image onto another image at position (x, y)."""
        if self.img is None or other_img.img is None:
            raise ValueError("Both images must be loaded before drawing.")

        # Ensure channel compatibility
        if self.img.shape[2] != other_img.img.shape[2]:
            if self.img.shape[2] == 3 and other_img.img.shape[2] == 4:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
            elif self.img.shape[2] == 4 and other_img.img.shape[2] == 3:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)

        h, w = self.img.shape[:2]
        H, W = other_img.img.shape[:2]

        if y + h > H or x + w > W:
            return  # Silently skip if doesn't fit

        roi = other_img.img[y:y + h, x:x + w]

        if self.img.shape[2] == 4:  # BGRA with alpha
            b, g, r, a = cv2.split(self.img)
            mask = a / 255.0
            for c in range(3):
                roi[..., c] = (1 - mask) * roi[..., c] + mask * self.img[..., c]
        else:  # BGR
            other_img.img[y:y + h, x:x + w] = self.img
        return self

    def show(self, window_name="Image"):
        """Display the image in a window."""
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow(window_name, self.img)
        return self
