import unittest
from datetime import date
from typing import Dict, Any
from flask import Flask
from models import Game, Publisher, Category, db

class TestModels(unittest.TestCase):
    """Test suite for model validations"""
    
    # Test data
    TEST_DATA: Dict[str, Any] = {
        "valid_publisher": {"name": "Test Publisher", "description": "A great publisher for testing"},
        "valid_category": {"name": "Strategy", "description": "Strategic games for testing"},
        "valid_game": {
            "title": "Test Game",
            "description": "An exciting test game with lots of features",
            "star_rating": 4.5
        }
    }

    def setUp(self) -> None:
        """Set up test database"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize in-memory database for testing
        db.init_app(self.app)
        
        # Create tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def test_game_title_too_short(self) -> None:
        """Test that game title validation rejects titles that are too short"""
        with self.app.app_context():
            # Create required publisher and category
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()
            
            # Attempt to create game with title that's too short
            with self.assertRaises(ValueError) as context:
                game = Game(
                    title="X",  # Only 1 character
                    description=self.TEST_DATA["valid_game"]["description"],
                    publisher=publisher,
                    category=category,
                    star_rating=4.0
                )
                db.session.add(game)
                db.session.commit()
            
            self.assertIn("Game title must be at least 2 characters", str(context.exception))

    def test_game_description_too_short(self) -> None:
        """Test that game description validation rejects descriptions that are too short"""
        with self.app.app_context():
            # Create required publisher and category
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()
            
            # Attempt to create game with description that's too short
            with self.assertRaises(ValueError) as context:
                game = Game(
                    title=self.TEST_DATA["valid_game"]["title"],
                    description="Too short",  # Only 9 characters
                    publisher=publisher,
                    category=category,
                    star_rating=4.0
                )
                db.session.add(game)
                db.session.commit()
            
            self.assertIn("Description must be at least 10 characters", str(context.exception))

    def test_valid_game_creation(self) -> None:
        """Test that a valid game can be created successfully"""
        with self.app.app_context():
            # Create required publisher and category
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()
            
            # Create valid game
            game = Game(
                title=self.TEST_DATA["valid_game"]["title"],
                description=self.TEST_DATA["valid_game"]["description"],
                publisher=publisher,
                category=category,
                star_rating=self.TEST_DATA["valid_game"]["star_rating"]
            )
            db.session.add(game)
            db.session.commit()
            
            # Verify game was created
            self.assertIsNotNone(game.id)
            self.assertEqual(game.title, self.TEST_DATA["valid_game"]["title"])
            self.assertEqual(game.description, self.TEST_DATA["valid_game"]["description"])
            self.assertEqual(game.star_rating, self.TEST_DATA["valid_game"]["star_rating"])

    def test_publisher_name_too_short(self) -> None:
        """Test that publisher name validation rejects names that are too short"""
        with self.app.app_context():
            # Attempt to create publisher with name that's too short
            with self.assertRaises(ValueError) as context:
                publisher = Publisher(name="X", description=self.TEST_DATA["valid_publisher"]["description"])
                db.session.add(publisher)
                db.session.commit()
            
            self.assertIn("Publisher name must be at least 2 characters", str(context.exception))

    def test_category_name_too_short(self) -> None:
        """Test that category name validation rejects names that are too short"""
        with self.app.app_context():
            # Attempt to create category with name that's too short
            with self.assertRaises(ValueError) as context:
                category = Category(name="X", description=self.TEST_DATA["valid_category"]["description"])
                db.session.add(category)
                db.session.commit()
            
            self.assertIn("Category name must be at least 2 characters", str(context.exception))

    def test_description_none_allowed(self) -> None:
        """Test that None descriptions are allowed for optional fields"""
        with self.app.app_context():
            # Create publisher without description
            publisher = Publisher(name=self.TEST_DATA["valid_publisher"]["name"], description=None)
            db.session.add(publisher)
            db.session.commit()
            
            # Verify publisher was created with None description
            self.assertIsNotNone(publisher.id)
            self.assertIsNone(publisher.description)

    def test_game_to_dict_serializes_relationships_and_optional_fields(self) -> None:
        """Test that game serialization includes related objects and nullable fields"""
        with self.app.app_context():
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()

            release_date = date(2025, 1, 15)
            game = Game(
                title=self.TEST_DATA["valid_game"]["title"],
                description=self.TEST_DATA["valid_game"]["description"],
                publisher=publisher,
                category=category,
                star_rating=self.TEST_DATA["valid_game"]["star_rating"],
                popularity=42,
                release_date=release_date,
            )
            db.session.add(game)
            db.session.commit()

            serialized_game = game.to_dict()

            self.assertEqual(serialized_game["title"], self.TEST_DATA["valid_game"]["title"])
            self.assertEqual(serialized_game["publisher"], {"id": publisher.id, "name": publisher.name})
            self.assertEqual(serialized_game["category"], {"id": category.id, "name": category.name})
            self.assertEqual(serialized_game["starRating"], self.TEST_DATA["valid_game"]["star_rating"])
            self.assertEqual(serialized_game["popularity"], 42)
            self.assertEqual(serialized_game["releaseDate"], release_date.isoformat())

    def test_game_to_dict_handles_missing_optional_relationships(self) -> None:
        """Test that game serialization preserves None values for optional fields"""
        with self.app.app_context():
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()

            game = Game(
                title=self.TEST_DATA["valid_game"]["title"],
                description=self.TEST_DATA["valid_game"]["description"],
                publisher=publisher,
                category=category,
                star_rating=None,
                popularity=None,
                release_date=None,
            )
            db.session.add(game)
            db.session.commit()

            serialized_game = game.to_dict()

            self.assertIsNone(serialized_game["starRating"])
            self.assertEqual(serialized_game["popularity"], 0)
            self.assertIsNone(serialized_game["releaseDate"])

    def test_publisher_and_category_to_dict_include_game_counts(self) -> None:
        """Test that publisher and category serialization report related game counts"""
        with self.app.app_context():
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()

            first_game = Game(
                title="Test Game Alpha",
                description="An exciting test game with lots of alpha features",
                publisher=publisher,
                category=category,
                star_rating=4.0,
            )
            second_game = Game(
                title="Test Game Beta",
                description="An exciting test game with lots of beta features",
                publisher=publisher,
                category=category,
                star_rating=4.8,
            )
            db.session.add_all([first_game, second_game])
            db.session.commit()

            self.assertEqual(publisher.to_dict()["game_count"], 2)
            self.assertEqual(category.to_dict()["game_count"], 2)

    def test_publisher_and_category_to_dict_return_zero_without_games(self) -> None:
        """Test that publisher and category serialization return zero when no games exist"""
        with self.app.app_context():
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()

            self.assertEqual(publisher.to_dict()["game_count"], 0)
            self.assertEqual(category.to_dict()["game_count"], 0)

if __name__ == '__main__':
    unittest.main()
