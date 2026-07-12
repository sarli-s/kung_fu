from chess.config import PIECE_KING, PIECE_PAWN, PIECE_QUEEN, COLOR_WHITE


class BoardRules:
    def prepare_piece(self, token, piece, board, fmt, from_row=None):
        pass

    def get_promotion(self, token, to_row, board, fmt):
        return None

    def is_royal(self, token, fmt):
        return False


class ChessBoardRules(BoardRules):
    def prepare_piece(self, token, piece, board, fmt, from_row=None):
        if fmt.piece_type(token) == PIECE_PAWN and from_row is not None:
            expected = (board.rows() - 2) if fmt.color(token) == COLOR_WHITE else 1
            piece.mover.start_row = from_row if from_row == expected else None

    def get_promotion(self, token, to_row, board, fmt):
        if fmt.piece_type(token) != PIECE_PAWN:
            return None
        last_row = 0 if fmt.color(token) == COLOR_WHITE else board.rows() - 1
        if to_row == last_row:
            return fmt.encode(fmt.color(token) + PIECE_QUEEN)
        return None

    def is_royal(self, token, fmt):
        return fmt.piece_type(token) == PIECE_KING
