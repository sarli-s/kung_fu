import cv2
import numpy as np
from pathlib import Path

pieces_dir = Path(r"c:\Users\User\Documents\שרלי\לימודים\בוטקאמפ בעזרת השם\kung fu\assets\images\pieces3")

for piece in ["wP", "wK", "bP", "bK"]:
    sprite_path = pieces_dir / piece / "states" / "idle" / "sprites" / "1.png"
    
    with open(str(sprite_path), 'rb') as f:
        img_data = np.frombuffer(f.read(), np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_UNCHANGED)
    
    print(f"{piece} original size: {img.shape}")
    
    # Resize to 100x100
    resized = cv2.resize(img, (100, 100), interpolation=cv2.INTER_AREA)
    print(f"{piece} resized size: {resized.shape}")
