from chess.ui.config import PIECE_STATE_MAP


class StateManager:
    @staticmethod
    def get_piece_state(engine, row, col):
        """Determine piece state based on engine conditions."""
        if engine.is_airborne(row, col):
            return PIECE_STATE_MAP["airborne"]
        elif engine.is_moving(row, col):
            return PIECE_STATE_MAP["moving"]
        # elif engine.is_short_rest(row, col):
        #     return PIECE_STATE_MAP["short_rest"]
        else:
            return PIECE_STATE_MAP["idle"]
