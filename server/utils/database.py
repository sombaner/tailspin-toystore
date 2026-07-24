import os
from sqlalchemy import inspect, text
from models import db, init_db as models_init_db

def init_db(app, connection_string=None, testing=False):
    """
    Initializes the database with the given Flask app and connection string.
    If no connection string is provided, a default SQLite connection string is used.
    
    Args:
        app: The Flask application instance
        connection_string: Optional database connection string
        testing: If True, allows reinitialization for testing
    """
    if connection_string is None:
        connection_string = __get_connection_string()
    app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    models_init_db(app, testing=testing)
    with app.app_context():
        _migrate_games_table()

def __get_connection_string():
    """
    Returns the connection string for the database.
    """
    # Get the server directory
    server_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Go up one level to project root, then into data folder
    project_root = os.path.dirname(server_dir)
    data_dir = os.path.join(project_root, "data")
    
    # Create the data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    return f'sqlite:///{os.path.join(data_dir, "tailspin-toys.db")}'


def _migrate_games_table() -> None:
    """Bring the legacy games table up to date for the current model."""
    inspector = inspect(db.engine)
    if "games" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("games")}
    migrations = []

    if "popularity" not in existing_columns:
        migrations.append("ALTER TABLE games ADD COLUMN popularity INTEGER DEFAULT 0")
    if "release_date" not in existing_columns:
        migrations.append("ALTER TABLE games ADD COLUMN release_date DATE")
    if "price" not in existing_columns:
        migrations.append("ALTER TABLE games ADD COLUMN price FLOAT DEFAULT 0.0")

    if not migrations:
        return

    with db.engine.begin() as connection:
        for statement in migrations:
            connection.execute(text(statement))

        if "popularity" not in existing_columns:
            connection.execute(text("UPDATE games SET popularity = COALESCE(popularity, 0)"))
        if "price" not in existing_columns:
            connection.execute(text("UPDATE games SET price = COALESCE(price, 0.0)"))