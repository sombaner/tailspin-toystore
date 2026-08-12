import os
import sqlite3
import tempfile
import unittest
from flask import Flask
from models import db
from utils.database import init_db


class TestDatabaseMigration(unittest.TestCase):
    """Test database migrations for legacy game schemas."""

    def setUp(self) -> None:
        """Create a legacy SQLite database file for migration tests."""
        handle = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = handle.name
        handle.close()

        connection = sqlite3.connect(self.db_path)
        connection.execute(
            """
            CREATE TABLE games (
                id INTEGER PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                star_rating FLOAT,
                category_id INTEGER NOT NULL,
                publisher_id INTEGER NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO games (title, description, star_rating, category_id, publisher_id)
            VALUES ('Legacy Game', 'A legacy record that must survive migration.', 4.0, 1, 1)
            """
        )
        connection.commit()
        connection.close()

        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{self.db_path}"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        init_db(self.app, connection_string=f"sqlite:///{self.db_path}", testing=True)

    def tearDown(self) -> None:
        """Dispose of the database and remove the temporary file."""
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()

        os.unlink(self.db_path)

    def test_legacy_games_table_is_upgraded(self) -> None:
        """Legacy game rows gain the columns needed by the API."""
        connection = sqlite3.connect(self.db_path)
        try:
            columns = [row[1] for row in connection.execute("PRAGMA table_info(games)")]
            self.assertIn("popularity", columns)
            self.assertIn("release_date", columns)
            self.assertIn("price", columns)

            row = connection.execute(
                "SELECT title, popularity, price, release_date FROM games WHERE title = ?",
                ("Legacy Game",),
            ).fetchone()
            self.assertEqual(row[0], "Legacy Game")
            self.assertEqual(row[1], 0)
            self.assertEqual(row[2], 0.0)
            self.assertIsNone(row[3])
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
