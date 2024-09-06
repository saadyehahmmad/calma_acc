import os
import logging
from flask import Flask

def create_app(config_filename=None):
    """
    Create and configure the Flask app instance.
    """
    # Create the Flask app
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Configure the app
    configure_app(app, config_filename)

    # Ensure necessary directories exist
    create_directories(app.config['UPLOAD_FOLDER'], app.config['STATIC_FOLDER'])

    # Import and register routes
    from .routes import register_routes
    register_routes(app)

    return app

def configure_app(app, config_filename=None):
    """
    Configure the app based on environment settings and custom configuration files.
    """
    # Absolute path for uploads in the production environment
    app.config['UPLOAD_FOLDER'] = os.path.abspath('uploads')
    app.config['STATIC_FOLDER'] = os.path.abspath('static')
    app.config['ALLOWED_EXTENSIONS'] = {'xlsx'}

    # Use environment variables to allow more flexibility in deployment
    app.config['ENV'] = os.getenv('FLASK_ENV', 'production')  # 'development' by default for dev
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    # Load additional configurations from a file, if provided
    if config_filename:
        try:
            app.config.from_pyfile(config_filename)
            logging.info(f"Configuration loaded from {config_filename}")
        except FileNotFoundError:
            logging.error(f"Config file {config_filename} not found, using default settings.")

    # If in development, you can still override the upload folder to something simpler
    if app.config['ENV'] == 'development':
        logging.info("Running in development mode")
        app.config['UPLOAD_FOLDER'] = os.path.abspath('dev_uploads')
    else:
        logging.info("Running in production mode")

def create_directories(*directories):
    """
    Ensure directories exist. If not, create them.
    """
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Directory ensured: {directory}")
        except OSError as e:
            logging.error(f"Error creating directory {directory}: {e}")

# Set up logging for the app
def setup_logging():
    """
    Set up logging for the application.
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO,  # Change to logging.DEBUG for more detailed logs
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logging.info("Logging is set up.")

# Call setup_logging when the module is imported
setup_logging()
