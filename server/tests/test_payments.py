import unittest
import json
from datetime import date
from typing import Dict, List, Any
from flask import Flask, Response
from models import Game, Publisher, Category, Cart, CartItem, Payment, db, init_db
from routes.cart import cart_bp
from routes.payments import payments_bp


class TestPaymentRoutes(unittest.TestCase):
    """Tests for the Payment API endpoints."""

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
    CHECKOUT_API_PATH: str = "/api/checkout"
    PAYMENTS_API_PATH: str = "/api/payments"

    def setUp(self) -> None:
        """Set up test database and seed data."""
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        self.app.register_blueprint(cart_bp)
        self.app.register_blueprint(payments_bp)

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

    def _create_cart_with_items(self, session_id: str = "checkout-session") -> None:
        """Helper to create a cart with items for checkout tests."""
        self.client.get(f"{self.CART_API_PATH}?session_id={session_id}")
        self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": session_id, "gameId": self.game_ids[0], "quantity": 1}),
            content_type="application/json",
        )
        self.client.post(
            f"{self.CART_API_PATH}/items",
            data=json.dumps({"sessionId": session_id, "gameId": self.game_ids[1], "quantity": 2}),
            content_type="application/json",
        )

    # --- POST /api/checkout ---

    def test_checkout_success(self) -> None:
        """Test POST checkout creates payment and marks cart as checked_out."""
        self._create_cart_with_items("pay-success")

        response = self.client.post(
            self.CHECKOUT_API_PATH,
            data=json.dumps({
                "sessionId": "pay-success",
                "paymentMethod": "credit_card",
                "cardLastFour": "1234",
            }),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 201)
        self.assertIn("transactionId", data)
        self.assertEqual(data["paymentMethod"], "credit_card")
        self.assertEqual(data["cardLastFour"], "1234")
        # Total should be 29.99*1 + 39.99*2 = 109.97
        self.assertAlmostEqual(data["amount"], 109.97, places=2)

    def test_checkout_empty_cart(self) -> None:
        """Test POST checkout with empty cart returns 400."""
        self.client.get(f"{self.CART_API_PATH}?session_id=empty-checkout")

        response = self.client.post(
            self.CHECKOUT_API_PATH,
            data=json.dumps({
                "sessionId": "empty-checkout",
                "paymentMethod": "credit_card",
                "cardLastFour": "1234",
            }),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)

    def test_checkout_invalid_session(self) -> None:
        """Test POST checkout with non-existent session returns 404."""
        response = self.client.post(
            self.CHECKOUT_API_PATH,
            data=json.dumps({
                "sessionId": "nonexistent-session-xyz",
                "paymentMethod": "credit_card",
                "cardLastFour": "1234",
            }),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", data)

    def test_checkout_invalid_payment_method(self) -> None:
        """Test POST checkout with invalid payment method returns 400."""
        self._create_cart_with_items("bad-method")

        response = self.client.post(
            self.CHECKOUT_API_PATH,
            data=json.dumps({
                "sessionId": "bad-method",
                "paymentMethod": "bitcoin",
                "cardLastFour": "1234",
            }),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)

    def test_checkout_already_checked_out(self) -> None:
        """Test POST checkout on already checked-out cart returns 400."""
        self._create_cart_with_items("double-checkout")

        self.client.post(
            self.CHECKOUT_API_PATH,
            data=json.dumps({
                "sessionId": "double-checkout",
                "paymentMethod": "credit_card",
                "cardLastFour": "1234",
            }),
            content_type="application/json",
        )

        response = self.client.post(
            self.CHECKOUT_API_PATH,
            data=json.dumps({
                "sessionId": "double-checkout",
                "paymentMethod": "credit_card",
                "cardLastFour": "5678",
            }),
            content_type="application/json",
        )
        data = self._get_response_data(response)

        # After first checkout, cart is no longer active, so second attempt gets 404
        self.assertIn(response.status_code, [400, 404])
        self.assertIn("error", data)

    # --- GET /api/payments/<transaction_id> ---

    def test_get_payment_status(self) -> None:
        """Test GET returns payment details by transaction ID."""
        self._create_cart_with_items("pay-status")

        checkout_resp = self.client.post(
            self.CHECKOUT_API_PATH,
            data=json.dumps({
                "sessionId": "pay-status",
                "paymentMethod": "credit_card",
                "cardLastFour": "4321",
            }),
            content_type="application/json",
        )
        checkout_data = self._get_response_data(checkout_resp)
        transaction_id = checkout_data["transactionId"]

        response = self.client.get(f"{self.PAYMENTS_API_PATH}/{transaction_id}")
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["transactionId"], transaction_id)
        self.assertEqual(data["cardLastFour"], "4321")

    def test_get_payment_not_found(self) -> None:
        """Test GET with non-existent transaction ID returns 404."""
        response = self.client.get(f"{self.PAYMENTS_API_PATH}/nonexistent-txn-id")
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
