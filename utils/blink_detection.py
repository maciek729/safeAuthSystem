import cv2
import mediapipe as mp
import numpy as np
import time
import face_recognition
import os

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

def get_eye_aspect_ratio(landmarks, eye_points):
    p = [landmarks[i] for i in eye_points]
    vertical1 = np.linalg.norm([p[1].x - p[5].x, p[1].y - p[5].y])
    vertical2 = np.linalg.norm([p[2].x - p[4].x, p[2].y - p[4].y])
    horizontal = np.linalg.norm([p[0].x - p[3].x, p[0].y - p[3].y])
    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return ear

def detect_blink_and_match_face():
    cap = cv2.VideoCapture(0)
    blink_detected = False
    start_time = time.time()
    captured_face = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                left_ear = get_eye_aspect_ratio(landmarks, LEFT_EYE)
                right_ear = get_eye_aspect_ratio(landmarks, RIGHT_EYE)
                avg_ear = (left_ear + right_ear) / 2

                if avg_ear < 0.22:  # mrugnięcie
                    blink_detected = True
                    captured_face = frame.copy()
                    break

        if blink_detected or (time.time() - start_time > 10):
            break

    cap.release()

    if not blink_detected or captured_face is None:
        return None  # brak autoryzacji

    # Porównanie twarzy z folderem
    unknown_encoding = face_recognition.face_encodings(captured_face)
    if not unknown_encoding:
        return None

    unknown_encoding = unknown_encoding[0]

    for filename in os.listdir("face_data"):
        if filename.endswith(".png"):
            known_image = face_recognition.load_image_file(os.path.join("face_data", filename))
            known_encoding = face_recognition.face_encodings(known_image)
            if known_encoding and face_recognition.compare_faces([known_encoding[0]], unknown_encoding)[0]:
                return filename.replace(".png", "")  # nazwa użytkownika

    return None
