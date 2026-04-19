from datetime import datetime, timezone
from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship


class Cart(BaseModel):
    """Represents a shopping cart session for a user."""

    __tablename__ = 'carts'

    VALID_STATUSES = ('active', 'checked_out', 'abandoned')

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), nullable=False, default='active')

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan", lazy='dynamic')
    payment = relationship("Payment", back_populates="cart", uselist=False)

    @validates('session_id')
    def validate_session_id(self, key: str, value: str) -> str:
        """Validate session_id is a non-empty string.

        Args:
            key: The field name.
            value: The session_id value.

        Returns:
            The validated session_id.
        """
        return self.validate_string_length('Session ID', value, min_length=2)

    @validates('status')
    def validate_status(self, key: str, value: str) -> str:
        """Validate status is one of the allowed values.

        Args:
            key: The field name.
            value: The status value.

        Returns:
            The validated status.
        """
        if value not in self.VALID_STATUSES:
            raise ValueError(f"Status must be one of {self.VALID_STATUSES}")
        return value

    def __repr__(self) -> str:
        return f'<Cart {self.id}, Session: {self.session_id}, Status: {self.status}>'

    def to_dict(self) -> dict:
        """Serialize the cart to a dictionary with camelCase keys.

        Returns:
            Dictionary representation of the cart including its items.
        """
        return {
            'id': self.id,
            'sessionId': self.session_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status,
            'items': [item.to_dict() for item in self.items] if self.items else [],
        }
