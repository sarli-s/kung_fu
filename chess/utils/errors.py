class ChessError(Exception):
    pass

class UnknownTokenError(ChessError):
    def __str__(self): return "ERROR UNKNOWN_TOKEN"

class RowWidthMismatchError(ChessError):
    def __str__(self): return "ERROR ROW_WIDTH_MISMATCH"
