import json
from pathlib import Path
from chess.ui.config import PIECES_DIR


class Animator:
    def __init__(self):
        self._animation_state = {}  # {(row, col, token, state): {"elapsed_ms": int, "frame_idx": int}}
        self._state_configs = {}  # {(token, state): config_dict}

    def _load_state_config(self, token, state):
        """Load animation config for a piece state."""
        cache_key = (token, state)
        if cache_key in self._state_configs:
            return self._state_configs[cache_key]
        
        config_path = PIECES_DIR / token / "states" / state / "config.json"
        if not config_path.exists():
            return None
        
        try:
            with open(str(config_path), 'r') as f:
                config = json.load(f)
            self._state_configs[cache_key] = config
            return config
        except:
            return None

    def _count_sprite_frames(self, token, state):
        """Count how many sprite frames exist for a state."""
        sprite_dir = PIECES_DIR / token / "states" / state / "sprites"
        if not sprite_dir.exists():
            return 0
        return len(list(sprite_dir.glob("*.png")))

    def get_frame_index(self, row, col, token, state, delta_ms):
        """Get current frame index for animation, updating elapsed time."""
        key = (row, col, token, state)
        
        # Initialize animation state if new
        if key not in self._animation_state:
            self._animation_state[key] = {"elapsed_ms": 0, "frame_idx": 0}
        
        anim = self._animation_state[key]
        anim["elapsed_ms"] += delta_ms
        
        # Get config and frame count
        config = self._load_state_config(token, state)
        if config is None:
            return 0
        
        fps = config.get("graphics", {}).get("frames_per_sec", 4)
        frame_duration_ms = 1000 // fps if fps > 0 else 250
        frame_count = self._count_sprite_frames(token, state)
        
        if frame_count == 0:
            return 0
        
        # Calculate frame index
        frame_idx = (anim["elapsed_ms"] // frame_duration_ms) % frame_count
        anim["frame_idx"] = frame_idx
        
        return frame_idx

    def clear_cache(self):
        """Clear animation state and config cache."""
        self._animation_state.clear()
        self._state_configs.clear()
