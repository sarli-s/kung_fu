import time


class MoveTracker:
    """Observer that tracks all moves made by each player."""
    
    def __init__(self):
        self.moves = {"white": [], "black": []}
        self.last_rendered_white = 0
        self.last_rendered_black = 0
    
    @staticmethod
    def _to_chess_notation(row, col):
        """Convert (row, col) to chess notation (e.g., 'a1', 'h8')."""
        col_letter = chr(ord('a') + col)
        row_number = 8 - row
        return f"{col_letter}{row_number}"
    
    def on_move(self, piece, from_row, from_col, to_row, to_col, **_):
        """Called when a piece moves. Extracts player color from piece token."""
        # Don't record blocked moves (where piece didn't actually move)
        if from_row == to_row and from_col == to_col:
            return
        
        color = piece[0]  # 'w' or 'b'
        player = "white" if color == "w" else "black"
        
        move_num = len(self.moves[player]) + 1
        from_notation = self._to_chess_notation(from_row, from_col)
        to_notation = self._to_chess_notation(to_row, to_col)
        
        move_entry = {
            "piece": piece,
            "from": (from_row, from_col),
            "to": (to_row, to_col),
            "from_notation": from_notation,
            "to_notation": to_notation,
            "move_num": move_num,
            "is_capture": False,
            "timestamp": time.time()
        }
        self.moves[player].append(move_entry)
    
    def mark_capture(self, to_row, to_col, capturing_piece=None):
        """Mark the capturing piece's last move to this position as a capture."""
        if not capturing_piece:
            return
        
        # Find which player made the capture
        capturing_color = capturing_piece[0]  # 'w' or 'b'
        capturing_player = "white" if capturing_color == "w" else "black"
        capturing_moves = self.moves[capturing_player]
        
        # Find the LAST move of the capturing piece that ends at this position
        for move in reversed(capturing_moves):
            if move["to"] == (to_row, to_col):
                move["is_capture"] = True
                return
    
    def get_moves(self, player):
        """Get all moves for a player ('white' or 'black')."""
        return self.moves.get(player, [])
    
    def get_new_moves(self, player):
        """Get only moves that haven't been rendered yet."""
        if player == "white":
            new_moves = self.moves["white"][self.last_rendered_white:]
            self.last_rendered_white = len(self.moves["white"])
        else:
            new_moves = self.moves["black"][self.last_rendered_black:]
            self.last_rendered_black = len(self.moves["black"])
        return new_moves
    
    def clear(self):
        """Clear all move history."""
        self.moves = {"white": [], "black": []}
        self.last_rendered_white = 0
        self.last_rendered_black = 0
