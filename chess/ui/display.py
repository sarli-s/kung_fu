import cv2
import time
from chess.core.controller import handle_commands, COMMAND_HANDLERS, _pixel_to_cell
from chess.ui.img import Img
from chess.ui.config import BOARD_SIZE, CELL_SIZE, BOARD_BORDER_X, BOARD_BORDER_Y


class DisplayLoop:
    def __init__(self, engine, renderer):
        self.engine = engine
        self.renderer = renderer
        self.ctx = {"selected": None, "game_over": False, "hover": None}
        # handle_commands will subscribe to on_game_over

    def _on_mouse_event(self, event, x, y, flags, param):
        """Handle both mouse move and click events."""
        if event == cv2.EVENT_MOUSEMOVE:
            cell = _pixel_to_cell(self.engine, x, y, border_x=BOARD_BORDER_X, border_y=BOARD_BORDER_Y)
            if cell is not None:
                self.ctx["hover"] = cell
            else:
                self.ctx["hover"] = None
        
        elif event == cv2.EVENT_LBUTTONDOWN:
            cell = _pixel_to_cell(self.engine, x, y, border_x=BOARD_BORDER_X, border_y=BOARD_BORDER_Y)
            if cell is None:
                return
            
            # Check if clicking the same cell that's already selected (double-click for jump)
            if self.ctx["selected"] is not None and self.ctx["selected"] == cell:
                # Send jump command
                row, col = cell
                handle_commands(self.engine, [f"jump {x} {y}"], handlers=COMMAND_HANDLERS, ctx=self.ctx)
            else:
                # Send regular click command
                handle_commands(self.engine, [f"click {x} {y}"], handlers=COMMAND_HANDLERS, ctx=self.ctx)

    def run(self):
        """Run the display loop. Press 'q' or ESC to exit."""
        cv2.namedWindow("Kung Fu Chess")
        cv2.setMouseCallback("Kung Fu Chess", self._on_mouse_event)
        
        last_time = time.perf_counter()
        
        while True:
            current_time = time.perf_counter()
            delta_ms = int((current_time - last_time) * 1000)
            last_time = current_time
            
            self.engine.advance(delta_ms)
            
            # Pass selected cell and delta_ms to renderer for animations
            canvas = self.renderer.render(self.engine, selected_cell=self.ctx["selected"], delta_ms=delta_ms)
            canvas_img = Img(canvas)
            
            # Draw hover highlight (gold border) always if hovering
            if self.ctx["hover"] is not None:
                row, col = self.ctx["hover"]
                x = col * CELL_SIZE + BOARD_BORDER_X
                y = row * CELL_SIZE + BOARD_BORDER_Y
                canvas_img.draw_rectangle(x, y, CELL_SIZE, CELL_SIZE, color=(0, 215, 255), thickness=3)  # Gold
            
            # Overlay game over text if game is over
            if self.engine.game_over:
                canvas_img.put_text("Game Over", BOARD_SIZE // 4, BOARD_SIZE // 2, 3.0, color=(0, 0, 255), thickness=3)
            
            canvas_img.show("Kung Fu Chess")
            
            key = cv2.waitKey(1)
            if key == ord('q') or key == 27:  # 'q' or ESC (don't mask with 0xFF to avoid false positives)
                break
        
        cv2.destroyAllWindows()
