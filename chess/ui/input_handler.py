import cv2
from chess.core.controller import handle_commands, COMMAND_HANDLERS, _pixel_to_cell
from chess.ui.config import BOARD_BORDER_X, BOARD_BORDER_Y, MARGINS_LEFT


class InputHandler:
    def __init__(self, engine, ctx):
        """
        Args:
            engine: GameEngine instance
            ctx: Shared state dict with keys: selected, hover, game_over
        """
        self.engine = engine
        self.ctx = ctx

    def on_mouse_event(self, event, x, y, flags, param):
        """Handle mouse events (move and click)."""
        # Adjust x coordinate for left panel margin
        x_adjusted = x - MARGINS_LEFT
        
        if event == cv2.EVENT_MOUSEMOVE:
            cell = _pixel_to_cell(self.engine, x_adjusted, y, border_x=BOARD_BORDER_X, border_y=BOARD_BORDER_Y)
            if cell is not None:
                self.ctx["hover"] = cell
            else:
                self.ctx["hover"] = None
        
        elif event == cv2.EVENT_LBUTTONDOWN:
            if self.engine.game_over:
                return
            
            cell = _pixel_to_cell(self.engine, x_adjusted, y, border_x=BOARD_BORDER_X, border_y=BOARD_BORDER_Y)
            if cell is None:
                return
            
            # Check if clicking the same cell that's already selected (double-click for jump)
            if self.ctx["selected"] is not None and self.ctx["selected"] == cell:
                # Send jump command
                row, col = cell
                handle_commands(self.engine, [f"jump {x_adjusted} {y}"], handlers=COMMAND_HANDLERS, ctx=self.ctx)
            else:
                # Send regular click command
                handle_commands(self.engine, [f"click {x_adjusted} {y}"], handlers=COMMAND_HANDLERS, ctx=self.ctx)
