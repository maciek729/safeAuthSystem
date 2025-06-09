from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from controllers.auth_controller import load_user

from routes.auth_routes import auth_blueprint
from routes.index_routes import index_blueprint

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_blueprint)
app.register_blueprint(index_blueprint)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.user_loader(load_user)
login_manager.login_view = 'auth.login'

if __name__ == '__main__':
    app.run(debug=True)
