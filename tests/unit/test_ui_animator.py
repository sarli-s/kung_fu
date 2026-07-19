import pytest
from unittest.mock import Mock, patch
from chess.ui.animator import Animator


def test_animator_init():
    animator = Animator()
    assert animator._animation_state == {}
    assert animator._state_configs == {}


def test_get_frame_index_new_animation():
    animator = Animator()
    
    with patch.object(animator, '_load_state_config') as mock_config:
        with patch.object(animator, '_count_sprite_frames', return_value=4):
            mock_config.return_value = {"graphics": {"frames_per_sec": 4}}
            
            frame_idx = animator.get_frame_index(0, 0, "wP", "idle", 100)
            
            assert frame_idx == 0
            assert (0, 0, "wP", "idle") in animator._animation_state


def test_get_frame_index_animation_progression():
    animator = Animator()
    
    with patch.object(animator, '_load_state_config') as mock_config:
        with patch.object(animator, '_count_sprite_frames', return_value=4):
            mock_config.return_value = {"graphics": {"frames_per_sec": 4}}
            
            frame1 = animator.get_frame_index(0, 0, "wP", "idle", 100)
            frame2 = animator.get_frame_index(0, 0, "wP", "idle", 200)
            
            assert frame1 == 0
            assert frame2 == 1


def test_clear_cache():
    animator = Animator()
    animator._animation_state[(0, 0, "wP", "idle")] = {"elapsed_ms": 100}
    animator._state_configs[("wP", "idle")] = {"graphics": {"frames_per_sec": 4}}
    
    animator.clear_cache()
    
    assert animator._animation_state == {}
    assert animator._state_configs == {}
