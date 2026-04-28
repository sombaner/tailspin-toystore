import unittest
import json
from datetime import date
from typing import Dict, Any
from flask import Flask, Response
from models import Game, Publisher, Category, db
from routes.games import games_bp

class TestGamesRoutes(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
            {"name": "Scrum Masters"}
        ],
        "categories": [
            {"name": "Strategy"},
            {"name": "Card Game"}
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5,
                "popularity": 500,
                "release_date": date(2025, 6, 15)
            },
            {
                "title": "Agile Adventures",
                "description": "Navigate your team through sprints and releases",
                "publisher_index": 1,
                "category_index": 1,
                "star_rating": 4.2,
                "popularity": 800,
                "release_date": date(2025, 9, 1)
            }
        ]
    }
    
    # API paths
    GAMES_API_PATH: str = '/api/games'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Register the games blueprint
        self.app.register_blueprint(games_bp)
        
        # Initialize the test client
        self.client = self.app.test_client()
        
        # Initialize in-memory database for testing
        db.init_app(self.app)
        
        # Create tables and seed data
        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data"""
        # Create test publishers
        publishers = [
            Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)
        
        # Create test categories
        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create test games
        games = []
        for game_data in self.TEST_DATA["games"]:
            game_dict = game_data.copy()
            publisher_index = game_dict.pop("publisher_index")
            category_index = game_dict.pop("category_index")
            
            games.append(Game(
                **game_dict,
                publisher=publishers[publisher_index],
                category=categories[category_index]
            ))
            
        db.session.add_all(games)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def test_get_games_success(self) -> None:
        """Test successful retrieval of multiple games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))

        titles = [game['title'] for game in data]
        self.assertEqual(titles, sorted(titles))

    def test_get_games_structure(self) -> None:
        """Test the response structure for games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))
        
        required_fields = ['id', 'title', 'description', 'publisher', 'category', 'starRating', 'popularity', 'releaseDate']
        for field in required_fields:
            self.assertIn(field, data[0])

    def test_get_game_by_id_success(self) -> None:
        """Test successful retrieval of a single game by ID"""
        # Get the first game's ID from the list endpoint
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        game_title = games[0]['title']
        
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/{game_id}')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], game_title)
        
    def test_get_game_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent game by ID"""
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/999')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

    def test_get_games_empty_database(self) -> None:
        """Test retrieval of games when database is empty"""
        # Clear all games from the database
        with self.app.app_context():
            db.session.query(Game).delete()
            db.session.commit()
        
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_search_games_by_title(self) -> None:
        """Test searching games by title returns matching results"""
        response = self.client.get(f'{self.GAMES_API_PATH}?search=Pipeline')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Pipeline Panic')

    def test_search_games_case_insensitive(self) -> None:
        """Test that search is case insensitive"""
        response = self.client.get(f'{self.GAMES_API_PATH}?search=pipeline')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Pipeline Panic')

    def test_search_games_trims_whitespace(self) -> None:
        """Test that search terms are trimmed before filtering results"""
        response = self.client.get(f'{self.GAMES_API_PATH}?search=  Pipeline  ')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Pipeline Panic')

    def test_search_games_no_results(self) -> None:
        """Test searching games with no matching results"""
        response = self.client.get(f'{self.GAMES_API_PATH}?search=nonexistent')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)

    def test_sort_by_popularity(self) -> None:
        """Test sorting games by popularity descending"""
        response = self.client.get(f'{self.GAMES_API_PATH}?sort=popularity')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data[0]['title'], 'Agile Adventures')
        self.assertEqual(data[1]['title'], 'Pipeline Panic')

    def test_sort_option_trims_whitespace(self) -> None:
        """Test sorting trims whitespace before applying supported options"""
        response = self.client.get(f'{self.GAMES_API_PATH}?sort= popularity ')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data[0]['title'], 'Agile Adventures')
        self.assertEqual(data[1]['title'], 'Pipeline Panic')

    def test_sort_by_rating(self) -> None:
        """Test sorting games by user rating descending"""
        response = self.client.get(f'{self.GAMES_API_PATH}?sort=rating')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data[0]['title'], 'Pipeline Panic')
        self.assertEqual(data[1]['title'], 'Agile Adventures')

    def test_sort_by_release_date(self) -> None:
        """Test sorting games by release date newest first"""
        response = self.client.get(f'{self.GAMES_API_PATH}?sort=release_date')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data[0]['title'], 'Agile Adventures')
        self.assertEqual(data[1]['title'], 'Pipeline Panic')

    def test_sort_invalid_option_falls_back_to_title_order(self) -> None:
        """Test invalid sort option falls back to title ordering"""
        response = self.client.get(f'{self.GAMES_API_PATH}?sort=invalid')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([game['title'] for game in data], ['Agile Adventures', 'Pipeline Panic'])

    def test_get_game_by_invalid_id_type(self) -> None:
        """Test retrieval of a game with invalid ID type"""
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/invalid-id')
        
        # Assert
        # Flask should return 404 for routes that don't match the <int:id> pattern
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()