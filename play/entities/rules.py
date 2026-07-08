from play.config import PIECE_KING, PIECE_PAWN, PIECE_QUEEN, COLOR_WHITE


class BoardRules:
    """
    Encapsulates game-specific rules that the Board engine delegates to.
    Override any method to customise behaviour for non-chess games.
    """

    def prepare_piece(self, token, piece, board, fmt):
        """Called before legality check. Mutate piece state as needed (e.g. set pawn direction)."""
        pass

    def get_promotion(self, token, to_row, board, fmt):
        """Return the replacement token string if a promotion occurs, else None."""
        return None

    def is_royal(self, token, fmt):
        """Return True if capturing this token ends the game."""
        return False


class ChessBoardRules(BoardRules):
    def prepare_piece(self, token, piece, board, fmt):
        if fmt.piece_type(token) == PIECE_PAWN:
            piece.mover.start_row = (board.rows() - 1) if fmt.color(token) == COLOR_WHITE else 0

    def get_promotion(self, token, to_row, board, fmt):
        if fmt.piece_type(token) != PIECE_PAWN:
            return None
        last_row = 0 if fmt.color(token) == COLOR_WHITE else board.rows() - 1
        if to_row == last_row:
            return fmt.encode(fmt.color(token) + PIECE_QUEEN)
        return None

    def is_royal(self, token, fmt):
        return fmt.piece_type(token) == PIECE_KING
