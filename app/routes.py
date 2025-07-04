from flask import Blueprint, jsonify, request, render_template, redirect, url_for, send_from_directory, flash
import os
from .db import insert_face, get_all_faces
import face_recognition
import numpy as np
import cv2
from werkzeug.utils import secure_filename
from PIL import Image

bp = Blueprint('main', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'videos')
RESULT_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'results')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        name = request.form['name']
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            # Extract face encoding
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                insert_face(name, np.array(encodings[0], dtype=np.float64))
                flash('Face encoding saved!')
            else:
                flash('No face found in the image.')
        return redirect(url_for('main.upload_image'))
    return render_template('upload_image.html')

@bp.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        file = request.files['video']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(VIDEO_FOLDER, filename)
            file.save(filepath)
            # Process video
            result_path = process_video(filepath)
            result_filename = os.path.basename(result_path)
            return render_template('show_result.html', video_file=url_for('static', filename=f'results/{result_filename}'))
    return render_template('upload_video.html')

def process_video(video_path):
    known_faces = get_all_faces()
    known_encodings = [encoding for _, encoding in known_faces]
    known_names = [name for name, _ in known_faces]
    cap = cv2.VideoCapture(video_path)
    result_path = os.path.join(RESULT_FOLDER, os.path.basename(video_path))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(result_path, fourcc, fps, (width, height))
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            if True in matches:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        out.write(frame)
    cap.release()
    out.release()
    return result_path
