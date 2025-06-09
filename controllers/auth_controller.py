from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, UserMixin
import sqlite3
from models.user import User
import os
import base64
from utils.blink_detection import * 


login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return User(user[0], user[1], user[2])  
    return None


def authenticate(username, password):
    if not detect_blink_and_match_face(): 
        print("Nie wykryto mrugnięcia.")
        return False

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[2], password):
        user_obj = User(user[0], user[1], user[2])
        login_user(user_obj)
        return True
    return False



def register_user(username, password, face_image_data=None):
    if not username or not password or not face_image_data:
        return "Wszystkie pola są wymagane."

    hashed_password = generate_password_hash(password).decode('utf-8')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # Sprawdź, czy użytkownik już istnieje
        cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            return "Użytkownik już istnieje."

        face_filename = f"{username}.png"
        cursor.execute('INSERT INTO users (username, password, face_image) VALUES (?, ?, ?)', 
                       (username, hashed_password, face_filename))
        conn.commit()

        # Zapisz zdjęcie
        header, encoded = face_image_data.split(",", 1)
        image_data = base64.b64decode(encoded)
        os.makedirs("face_data", exist_ok=True)
        save_path = os.path.join("face_data", f"{username}.png")
        with open(save_path, "wb") as f:
            f.write(image_data)

        return True

    finally:
        conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return User(user[0], user[1], user[2])  # zakładamy, że to User(id, username, password)
    return None



#kontrolery do listy użytkowników

def getUsersData(selectId):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = '''
    SELECT users.firstName || ' ' || users.lastName AS fullName, 
           users.phoneNumber, users.address, users.email
    FROM users
    WHERE users.profession = ?
    '''
    cursor.execute(query, (selectId,))
    users_data = cursor.fetchall()  
    conn.close()

    result = [
        {
            "fullName": row[0],
            "phoneNumber": row[1],
            "address": row[2],
            "email": row[3]
        }
        for row in users_data
    ]

    return result