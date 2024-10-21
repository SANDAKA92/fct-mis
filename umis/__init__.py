from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # App configuration
    app.config['SECRET_KEY'] = 'ConFct@4312'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable to avoid unnecessary warnings

    # Initialize database
    db.init_app(app)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Assuming the login route is in 'auth'
    login_manager.init_app(app)

    # User loader callback for login
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from .auth import auth as auth_blueprint  # Assuming 'auth' is the authentication blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint  # Main application routes
    app.register_blueprint(main_blueprint)

    # Import the create_admin CLI command to ensure it's registered
    from .auth import create_admin  # Import the CLI command to register it

    return app

