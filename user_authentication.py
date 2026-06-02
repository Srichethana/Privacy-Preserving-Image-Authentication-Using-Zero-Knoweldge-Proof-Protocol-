import json
import os
from image_preprocessing import preprocess_image, generate_image_hash
DATABASE = "users.json"
USED_IMAGES_FILE = "used_images.json"
def load_used_images():
    try:
        with open(USED_IMAGES_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()
def save_used_images(used_set):
    with open(USED_IMAGES_FILE, "w") as f:
        json.dump(list(used_set), f)
used_images = load_used_images()
def load_users():
    try:
        with open(DATABASE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
def save_users(users):
    with open(DATABASE, "w") as file:
        json.dump(users, file, indent=4)
def register(username: str, image_path: str):
    users = load_users()
    if username in users:
        return False, "Patient ID already exists!"
    try:
        processed_image = preprocess_image(image_path)
        image_hash = generate_image_hash(processed_image)
        if image_hash in used_images:
            return False, "This image has already been used by another patient. Please use a different image."
        users[username] = image_hash
        save_users(users)
        used_images.add(image_hash)
        save_used_images(used_images)        
        return True, f"Patient {username} registered successfully!"
    except Exception as e:
        return False, f"Error processing image: {str(e)}"