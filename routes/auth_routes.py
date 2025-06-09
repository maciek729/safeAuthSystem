from flask import Blueprint, render_template, request, redirect, flash, url_for,jsonify
from controllers.auth_controller import *
from flask_login import login_required, logout_user, current_user
from routes.index_routes import index
import face_recognition
import os
import base64
from utils.blink_detection import detect_blink_and_match_face



auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            return redirect(url_for('index.index'))
        else:
            flash('Nieprawidłowy login lub hasło.')
    return render_template('login.html')

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        face_image = request.form.get('faceImage')

        result = register_user(username, password, face_image)
        if result is True:
            return redirect(url_for('auth.login'))
        else:
            flash(result)  # pokaże komunikat, np. "Użytkownik już istnieje." albo "Brakuje zdjęcia"
            return redirect(url_for('auth.register'))

    return render_template('register.html')



@auth_blueprint.route('/face-login', methods=['POST'])
def face_login():
    try:
        username = detect_blink_and_match_face()  # to nowa funkcja w osobnym pliku
        if username:
            user = get_user_by_username(username)
            if user:
                login_user(user)
                return jsonify({"success": True}), 200
        return jsonify({"success": False, "message": "Nie rozpoznano twarzy lub brak mrugnięcia"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

