import base64
import numpy as np
from deepface import DeepFace
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import firebase_admin
from firebase_admin import firestore
import re
import cv2


# Initialize Firestore client (ensure Firebase is initialized)
db = firestore.client()

def clean_base64_image(base64_str):
    match = re.match(r'data:image/\w+;base64,(.*)', base64_str)
    return match.group(1) if match else base64_str

def register_face(user_id, face_image):
    """
    Register a face image in Firestore for a specific user.
    """
    try:
        # Clean the base64 string
        cleaned_image = clean_base64_image(face_image)

        # Optional: Check if it's a valid image
        decoded = base64.b64decode(cleaned_image)
        Image.open(BytesIO(decoded))  # Will raise error if invalid

        user_ref = db.collection('users').document(user_id)
        user_ref.set({
            'face_image': cleaned_image
        }, merge=True)

        return True
    except Exception as e:
        print(f"Error in registering face: {e}")
        return False

def is_valid_base64_image(base64_str):
    try:
        decoded = base64.b64decode(base64_str)
        Image.open(BytesIO(decoded))
        return True
    except:
        return False

def decode_base64_image(base64_str):
    # Remove base64 header if exists
    match = re.match(r'data:image/\w+;base64,(.*)', base64_str)
    if match:
        base64_str = match.group(1)
    return base64.b64decode(base64_str)

def recognize_face(face_image):
    """
    Recognize the face from the captured image and return the user ID.
    """
    try:
        captured_image_data = decode_base64_image(face_image)

        try:
            captured_image = Image.open(BytesIO(captured_image_data))
        except Exception as e:
            print(f"Error in decoding the captured face image: {e}")
            return None

        users_ref = db.collection('users')
        users = users_ref.stream()

        for user in users:
            user_data = user.to_dict()
            stored_face_base64 = user_data.get('face_image')

            if not stored_face_base64 or not is_valid_base64_image(stored_face_base64):
                print(f"Invalid or missing face image for user: {user.id}")
                continue

            try:
                stored_image_data = base64.b64decode(stored_face_base64)
                stored_image = Image.open(BytesIO(stored_image_data))

                # Convert both to BGR arrays for DeepFace
                captured_image_np = cv2.cvtColor(np.array(captured_image), cv2.COLOR_RGB2BGR)
                stored_image_np = cv2.cvtColor(np.array(stored_image), cv2.COLOR_RGB2BGR)

                result = DeepFace.verify(captured_image_np, stored_image_np)

                if result["verified"]:
                    return user.id
            except Exception as e:
                print(f"Error with user {user.id} face image comparison: {e}")
                continue

        return None
    except Exception as e:
        print(f"Error in recognizing face: {e}")
        return None
