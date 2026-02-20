import os
from flask import Flask
from routes.games import games_bp
from routes.debug import debug_bp
from utils.database import init_db
from utils.logging_config import setup_logging, add_request_logging_middleware

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)

# Initialize structured logging
setup_logging(app)
add_request_logging_middleware(app)

# Initialize the database with the app
init_db(app)

# Register API blueprints
app.register_blueprint(games_bp)

# Enable debug endpoints only if explicitly allowed
if os.getenv('ENABLE_DEBUG_ENDPOINTS', 'false').lower() in ('1', 'true', 'yes'):
    app.register_blueprint(debug_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5100)  # Bind to all interfaces for containers