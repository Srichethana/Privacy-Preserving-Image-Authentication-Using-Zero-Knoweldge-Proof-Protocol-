import cv2
import numpy as np
import hashlib
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found! Check the path.")
    image = cv2.resize(image, (128, 128))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    normalized = gray / 255.0
    return normalized
def generate_image_hash(processed_image):
    image_bytes = processed_image.tobytes()
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    return image_hash