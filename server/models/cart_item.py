from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship


class CartItem(BaseModel):
    """Represents an item in a shopping cart, linking a cart to a game."""

    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    cart = relationship("Cart", back_populates="items")
    game = relationship("Game")

    @validates('quantity')
    def validate_quantity(self, key: str, value: int) -> int:
        """Validate quantity is at least 1.

        Args:
            key: The field name.
            value: The quantity value.

        Returns:
            The validated quantity.
        """
        if not isinstance(value, int) or value < 1:
            raise ValueError("Quantity must be an integer of at least 1")
        return value

    @validates('price')
    def validate_price(self, key: str, value: float) -> float:
        """Validate price is non-negative.

        Args:
            key: The field name.
            value: The price value.

        Returns:
            The validated price.
        """
        if value is None or value < 0:
            raise ValueError("Price must be a non-negative number")
        return value

    def __repr__(self) -> str:
        return f'<CartItem {self.id}, Cart: {self.cart_id}, Game: {self.game_id}, Qty: {self.quantity}>'

    def to_dict(self) -> dict:
        """Serialize the cart item to a dictionary with camelCase keys.

        Returns:
            Dictionary representation of the cart item including the game title.
        """
        return {
            'id': self.id,
            'cartId': self.cart_id,
            'gameId': self.game_id,
            'gameTitle': self.game.title if self.game else None,
            'quantity': self.quantity,
            'price': self.price,
        }
