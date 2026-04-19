import unittest
import json
from datetime import date
from typing import Dict, List, Any
from flask import Flask, Response
from models import Game, Publisher, Category, Cart, CartItem, db, init_db
from routes.cart import cart_bp


class TestCartRoutes(unittest.TestCase):
    """Tests for the Cart API endpoints."""

    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
        ],
        "categories": [
            {"name": "Strategy"},
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5,
                "popularity": 500,
                "release_date": date(2025, 6, 15),
                "price": 29.99,
            },
            {
                "title": "Agile Adventures",
                "description": "Navigate your team through sprints and releases",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.2,
                "popularity": 800,
                "release_date": date(2025, 9, 1),
                "price": 39.99,
            },
        ],
    }

    CART_API_PATH: str = "/api/cart"

    def setUp(self) -> None:
        """Set up test database and seed data."""
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        self.app.register_blueprint(cart_bp)

        self.client = self.app.test_client()

        init_db(self.app, testing=True)

        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data."""
        publishers = [
            Publisher(**p) for p in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)

        categories = [
            Category(**c) for c in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)
        db.session.commit()

        games = []
        for game_data in self.TEST_DATA["games"]:
            gd = game_data.copy()
            pi = gd.pop("publisher_index")
            ci = gd.pop("category_index")
            games.append(Game(**gd, publisher=publishers[pi], category=categories[ci]))
        db.session.add_all(games)
        db.session.commit()

        self.game_ids = [g.id for g in games]

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data."""
        return json.loads(response.data)

    # --- GET /api/cart ---

    def test_get_cart_creates_new_cart(self) -> None:
        """Test GET with a new session_id creates a fresh cart."""
        response = self.client.get(f"{self.CART_API_PATH}?session_id=new-session-123")
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["sessionId"], "new-session-123")
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["items"], [])

    def test_get_cart_returns_existing(self) -> None:
        """Test GET with an existing session_id returns the same cart."""
        resp1 = self.client.get(f"{self.CART_API_PATH}?session_id=repeat-session")
        data1 = self._get_response_data(resp1)

        resp2 = self.client.get(f"{self.CART_API_PATH}?session_id=repeat-session")
        data2 = self._get_response_data(resp2)

        self.assertEqual(data1["id"], data2["id"])
        self.assertEqual(data1["sessionId"], data2["sessionId"])

    def test_get_cart_missing_session_id(self) -> None:
        """Test GET without session_id returns 400."""
        response = self.client.get(self.CART_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)

    # --- POST /api/cart/items ---

    def test_add_item_to_cart(self) -> None:
        """Test POST adds an item to cart with correct price snapshot."""
        # Create cart first
        self.client.get(f"{self.CART_API_PATH}?session_id=cart-add-item")

        response = self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": "cart-add-item", "gameId": self.game_ids[0], "quantity": 1}),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 201)
        # Route returns full cart; verify the item is present
        self.assertEqual(len(data["items"]), 1)
        item = data["items"][0]
        self.assertEqual(item["gameId"], self.game_ids[0])
        self.assertEqual(item["quantity"], 1)
        self.assertEqual(item["price"], 29.99)

    def test_add_item_increments_quantity(self) -> None:
        """Test POST with same game increments quantity."""
        self.client.get(f"{self.CART_API_PATH}?session_id=cart-incr")

        self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": "cart-incr", "gameId": self.game_ids[0], "quantity": 1}),
            content_type="application/json",
        )
        response = self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": "cart-incr", "gameId": self.game_ids[0], "quantity": 2}),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        self.assertIn(response.status_code, [200, 201])
        # Find the item for game_ids[0] in the cart
        matching = [i for i in data["items"] if i["gameId"] == self.game_ids[0]]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["quantity"], 3)

    def test_add_item_invalid_game(self) -> None:
        """Test POST with non-existent game returns 404."""
        self.client.get(f"{self.CART_API_PATH}?session_id=cart-bad-game")

        response = self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": "cart-bad-game", "gameId": 9999, "quantity": 1}),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", data)

    def test_add_item_missing_fields(self) -> None:
        """Test POST with missing required fields returns 400."""
        response = self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": "cart-missing"}),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)

    # --- PUT /api/cart/items/<item_id> ---

    def test_update_item_quantity(self) -> None:
        """Test PUT changes quantity of a cart item."""
        self.client.get(f"{self.CART_API_PATH}?session_id=cart-update")
        add_resp = self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": "cart-update", "gameId": self.game_ids[0], "quantity": 1}),
            content_type="application/json",
        )
        add_data = self._get_response_data(add_resp)
        item_id = add_data["items"][0]["id"]

        response = self.client.put(
            f"{self.CART_API_PATH}/items/{item_id}",
            data=json.dumps({"quantity": 5}),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["items"][0]["quantity"], 5)

    def test_update_item_quantity_zero_removes(self) -> None:
        """Test PUT with quantity 0 removes the item."""
        self.client.get(f"{self.CART_API_PATH}?session_id=cart-zero")
        add_resp = self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": "cart-zero", "gameId": self.game_ids[0], "quantity": 1}),
            content_type="application/json",
        )
        item_id = self._get_response_data(add_resp)["items"][0]["id"]

        response = self.client.put(
            f"{self.CART_API_PATH}/items/{item_id}",
            data=json.dumps({"quantity": 0}),
            content_type="application/json",
        )

        self.assertIn(response.status_code, [200, 204])

    def test_update_item_not_found(self) -> None:
        """Test PUT on non-existent item returns 404."""
        response = self.client.put(
            f"{self.CART_API_PATH}/items/9999",
            data=json.dumps({"quantity": 2}),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", data)

    # --- DELETE /api/cart/items/<item_id> ---

    def test_remove_item(self) -> None:
        """Test DELETE removes item from cart."""
        self.client.get(f"{self.CART_API_PATH}?session_id=cart-remove")
        add_resp = self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": "cart-remove", "gameId": self.game_ids[0], "quantity": 1}),
            content_type="application/json",
        )
        item_id = self._get_response_data(add_resp)["items"][0]["id"]

        response = self.client.delete(f"{self.CART_API_PATH}/items/{item_id}")

        self.assertIn(response.status_code, [200, 204])

    def test_remove_item_not_found(self) -> None:
        """Test DELETE on non-existent item returns 404."""
        response = self.client.delete(f"{self.CART_API_PATH}/items/9999")
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", data)

    # --- GET /api/cart/count ---

    def test_get_cart_count(self) -> None:
        """Test GET count returns total quantity across items."""
        self.client.get(f"{self.CART_API_PATH}?session_id=cart-count")
        self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": "cart-count", "gameId": self.game_ids[0], "quantity": 2}),
            content_type="application/json",
        )
        self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": "cart-count", "gameId": self.game_ids[1], "quantity": 3}),
            content_type="application/json",
        )

        response = self.client.get(f"{self.CART_API_PATH}/count?session_id=cart-count")
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 5)

    def test_get_cart_count_empty(self) -> None:
        """Test GET count for empty/new cart returns 0."""
        response = self.client.get(f"{self.CART_API_PATH}/count?session_id=empty-cart-session")
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 0)


if __name__ == "__main__":
    unittest.main()
