import pytest
from unittest.mock import Mock, patch
from chess.ui.assets import AssetLoader


def test_asset_loader_init():
    loader = AssetLoader()
    assert loader._sprite_cache == {}
    assert loader._square_image is None
    assert loader._board_bg is None


def test_clear_cache():
    loader = AssetLoader()
    loader._sprite_cache[("wP", "idle", 0)] = Mock()
    loader._square_image = Mock()
    loader._board_bg = Mock()
    
    loader.clear_cache()
    
    assert loader._sprite_cache == {}
    assert loader._square_image is None
    assert loader._board_bg is None


@patch('chess.ui.assets.cv2.imdecode')
@patch('builtins.open', create=True)
def test_get_board_background_caching(mock_open, mock_imdecode):
    import numpy as np
    mock_img = np.zeros((808, 808, 3), dtype=np.uint8)
    mock_imdecode.return_value = mock_img
    mock_open.return_value.__enter__.return_value.read.return_value = b'fake_data'
    
    loader = AssetLoader()
    result1 = loader.get_board_background()
    result2 = loader.get_board_background()
    
    assert result1 is result2
    assert mock_imdecode.call_count == 1
