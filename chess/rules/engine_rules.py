from chess.config import PIECE_KING, PIECE_PAWN, PIECE_QUEEN, COLOR_WHITE


class BoardRules:
    def prepare_piece(self, token, piece, board, fmt):
        pass

    def get_promotion(self, token, to_row, board, fmt):
        return None

    def is_royal(self, token, fmt):
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
