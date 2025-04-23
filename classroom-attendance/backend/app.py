from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_config import initialize_firebase
from face_recognition import register_face, recognize_face
from utils.firebase_utils import add_user_to_firestore, update_attendance

app = Flask(__name__)

# Initialize Firebase
firebase_app = initialize_firebase()

# Enable CORS for the app
CORS(app, origins="http://127.0.0.1:5500")

@app.route('/register_face', methods=['POST'])
def register_face_endpoint():
    """
    Endpoint to register the face of a student during registration.
    The face image should be sent in the request body as base64.
    """
    data = request.json
    user_id = data['user_id']
    face_image = data['face_image']  # base64 encoded image string
    
    success = register_face(user_id, face_image)
    
    if success:
        return jsonify({"message": "Face registered successfully."}), 200
    else:
        return jsonify({"message": "Face registration failed."}), 500

@app.route('/recognize_face', methods=['POST'])
def recognize_face_endpoint():
    """
    Endpoint to recognize a face during the attendance marking process.
    """
    face_image = request.json['face_image']  # Captured face image in base64
    
    recognized_user_id = recognize_face(face_image)
    
    if recognized_user_id:
        return jsonify({"user_id": recognized_user_id, "message": "Attendance marked."}), 200
    else:
        return jsonify({"message": "Face not recognized."}), 400

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    """
    Endpoint to mark attendance for a student.
    """
    data = request.json
    user_id = data['user_id']
    date = data['date']
    status = data['status']  # 'Present' or 'Absent'
    
    success = update_attendance(user_id, date, status)
    
    if success:
        return jsonify({"message": "Attendance marked successfully."}), 200
    else:
        return jsonify({"message": "Failed to mark attendance."}), 500

@app.route('/register_user', methods=['POST'])
def register_user():
    """
    Endpoint to register a student or teacher in Firestore.
    """
    data = request.json
    name = data['name']
    email = data['email']
    role = data['role']  # 'student' or 'teacher'
    
    user_id = add_user_to_firestore(name, email, role)
    
    if user_id:
        return jsonify({"message": "User registered successfully.", "user_id": user_id}), 200
    else:
        return jsonify({"message": "Failed to register user."}), 500

if __name__ == '__main__':
    app.run(debug=True)
