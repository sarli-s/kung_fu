import cv2
import numpy as np
import time
from chess.ui.input_handler import InputHandler
from chess.ui.img import Img
from chess.ui.config import BOARD_SIZE, CELL_SIZE, BOARD_BORDER_X, BOARD_BORDER_Y, MARGINS_LEFT


class DisplayLoop:
    def __init__(self, engine, renderer):
        self.engine = engine
        self.renderer = renderer
        self.ctx = {"selected": None, "game_over": False, "hover": None}
        self.input_handler = InputHandler(engine, self.ctx)
        # handle_commands will subscribe to on_game_over

    def run(self):
        """Run the display loop. Press 'q' or ESC to exit."""
        cv2.namedWindow("Kung Fu Chess")
        cv2.setMouseCallback("Kung Fu Chess", self.input_handler.on_mouse_event)
        
        last_time = time.perf_counter()
        
        while True:
            current_time = time.perf_counter()
            delta_ms = int((current_time - last_time) * 1000)
            last_time = current_time
            
            self.engine.advance(delta_ms)
            
            # Pass selected cell and delta_ms to renderer for animations
            board_canvas = self.renderer.render(self.engine, selected_cell=self.ctx["selected"], delta_ms=delta_ms)
            board_height = board_canvas.shape[0]
            
            canvas_img = Img(board_canvas)
            
            # Draw hover highlight (gold border) always if hovering
            if self.ctx["hover"] is not None:
                row, col = self.ctx["hover"]
                x = col * CELL_SIZE + BOARD_BORDER_X + MARGINS_LEFT
                y = row * CELL_SIZE + BOARD_BORDER_Y
                canvas_img.draw_rectangle(x, y, CELL_SIZE, CELL_SIZE, color=(0, 215, 255), thickness=3)  # Gold
            
            # Overlay game over text if game is over
            if self.engine.game_over:
                canvas_img.put_text("Game Over", BOARD_SIZE // 4 + MARGINS_LEFT, BOARD_SIZE // 2, 3.0, color=(0, 0, 255), thickness=3)
            
            canvas_img.show("Kung Fu Chess")
            
            key = cv2.waitKey(1)
            if key == ord('q') or key == 27:  # 'q' or ESC (don't mask with 0xFF to avoid false positives)
                break
        
        cv2.destroyAllWindows()
