class UIError(Exception):
    pass


class AssetLoadError(UIError):
    pass


class ImageError(UIError):
    pass


class AnimationError(UIError):
    pass
