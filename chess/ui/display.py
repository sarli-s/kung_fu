import cv2
import numpy as np
import time
from chess.ui.input_handler import InputHandler
from chess.ui.img import Img
from chess.ui.config import BOARD_SIZE, CELL_SIZE, BOARD_BORDER_X, BOARD_BORDER_Y, MARGINS_LEFT


class DisplayLoop:
    def __init__(self, engine, renderer, title="Kung Fu Chess", my_color=None, player_names=None):
        self.engine = engine
        self.renderer = renderer
        self.title = title
        self.player_names = player_names if player_names is not None else {}
        self.ctx = {"selected": None, "game_over": False, "hover": None, "winner": None}
        engine.subscribe("on_game_over", self._on_game_over)
        self.input_handler = InputHandler(engine, self.ctx, my_color=my_color)
        self._start_time = time.perf_counter()

    def _on_game_over(self, winner=None, **_):
        color_names = {"w": "White", "b": "Black"}
        self.ctx["winner"] = color_names.get(winner, winner)

    def run(self):
        cv2.namedWindow(self.title)
        cv2.setMouseCallback(self.title, self.input_handler.on_mouse_event)
        
        last_time = time.perf_counter()
        
        while True:
            current_time = time.perf_counter()
            delta_ms = int((current_time - last_time) * 1000)
            last_time = current_time
            
            if not self.engine.game_over:
                self.engine.advance(delta_ms)
            
            elapsed_ms = (current_time - self._start_time) * 1000

            scores = getattr(self.engine, 'scores', None)
            if scores is None and hasattr(self.engine, 'move_tracker'):
                scores = self.engine.move_tracker.scores
            engine_elapsed = getattr(self.engine, 'elapsed_ms', None)
            if engine_elapsed is not None:
                elapsed_ms = engine_elapsed

            board_canvas = self.renderer.render(
                self.engine, selected_cell=self.ctx["selected"], delta_ms=delta_ms,
                player_names=self.player_names, scores=scores or {}, elapsed_ms=elapsed_ms
            )
            board_height = board_canvas.shape[0]
            
            canvas_img = Img(board_canvas)
            
            if self.ctx["hover"] is not None:
                row, col = self.ctx["hover"]
                x = col * CELL_SIZE + BOARD_BORDER_X + MARGINS_LEFT
                y = row * CELL_SIZE + BOARD_BORDER_Y
                canvas_img.draw_rectangle(x, y, CELL_SIZE, CELL_SIZE, color=(0, 215, 255), thickness=3)
            
            if self.engine.game_over:
                winner = self.ctx["winner"]
                winner_name = self.player_names.get(winner, winner.capitalize() if winner else "")
                canvas_img.put_text(f"GAME OVER!!", BOARD_SIZE // 4 + MARGINS_LEFT // 2, BOARD_SIZE // 2, 3.0, color=(0, 0, 255), thickness=3)
            
            canvas_img.show(self.title)
            
            key = cv2.waitKey(1)
            if key == ord('q') or key == 27:  # 0xFF mask omitted — it causes false positives on some Linux/macOS backends
                break
            if cv2.getWindowProperty(self.title, cv2.WND_PROP_VISIBLE) < 1:
                break
        
        cv2.destroyAllWindows()
