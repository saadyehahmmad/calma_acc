import os
from flask import Flask
from flask_socketio import SocketIO

# Create a global SocketIO instance
socketio = SocketIO()

def create_app(config_filename=None):
    # Create a Flask app instance, specifying the template folder if needed
    app = Flask(__name__, template_folder='../templates', static_folder='../static')  # Only specify if your template folder is custom

    # Load configuration
    configure_app(app, config_filename)

    # Ensure the upload folder exists
    create_directories(app.config['UPLOAD_FOLDER'])

    # Initialize SocketIO with the app
    socketio.init_app(app)

    # Import and register routes and SocketIO events for both functionalities
    from .routes import register_routes
    from .totc import register_totc_routes
    from .matcher import register_matcher_routes
    register_routes(app, socketio)
    register_totc_routes(app, socketio)
    register_matcher_routes(app, socketio)

    return app

def configure_app(app, config_filename):
    # Default configuration
    app.config['UPLOAD_FOLDER'] = os.path.abspath('uploads/daily_inventory')
    app.config['STATIC_FOLDER'] = os.path.abspath('static')
    app.config['ALLOWED_EXTENSIONS'] = {'xlsx'}
    
    # Load configuration from a file, if provided
    if config_filename:
        app.config.from_pyfile(config_filename)

def create_directories(*directories):
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Directory created: {directory}")
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")