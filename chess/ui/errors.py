class UIError(Exception):
    """Base exception for UI-related errors."""
    pass


class AssetLoadError(UIError):
    """Raised when asset loading fails."""
    pass


class ImageError(UIError):
    """Raised when image operations fail."""
    pass


class AnimationError(UIError):
    """Raised when animation operations fail."""
    pass
