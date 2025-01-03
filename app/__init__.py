from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.debug = True

    # Import configuration
    from config import Config
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints after db initialization to avoid circular imports
    from .routes.auth import auth_bp
    from .routes.otp import otp_bp
    from .routes.profile import profile_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(otp_bp, url_prefix="/otp")
    app.register_blueprint(profile_bp, url_prefix="/profile")

    return app
