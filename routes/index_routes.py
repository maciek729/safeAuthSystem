from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta


index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username)
