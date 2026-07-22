import cv2
from chess.core.controller import handle_commands, COMMAND_HANDLERS, _pixel_to_cell
from chess.ui.config import BOARD_BORDER_X, BOARD_BORDER_Y, MARGINS_LEFT


class InputHandler:
    def __init__(self, engine, ctx, my_color=None):
        self.engine = engine
        self.ctx = ctx
        self.my_color = my_color

    def on_mouse_event(self, event, x, y, flags, param):
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
            
            row, col = cell
            token = self.engine.cell(row, col)
            # if my_color is set, block selecting enemy pieces
            if self.my_color and token != "." and not token.startswith(self.my_color):
                self.ctx["selected"] = None
                return
            
            if self.ctx["selected"] is not None and self.ctx["selected"] == cell:
                handle_commands(self.engine, [f"jump {x_adjusted} {y}"], handlers=COMMAND_HANDLERS, ctx=self.ctx)
            else:
                handle_commands(self.engine, [f"click {x_adjusted} {y}"], handlers=COMMAND_HANDLERS, ctx=self.ctx)
