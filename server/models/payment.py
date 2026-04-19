import uuid
from datetime import datetime, timezone
from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship


class Payment(BaseModel):
    """Represents a payment transaction associated with a cart checkout."""

    __tablename__ = 'payments'

    VALID_STATUSES = ('pending', 'completed', 'failed', 'refunded')
    VALID_METHODS = ('credit_card', 'debit_card', 'paypal')

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    card_last_four = db.Column(db.String(4), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    transaction_id = db.Column(db.String(36), unique=True, nullable=False,
                               default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    cart = relationship("Cart", back_populates="payment")

    @validates('amount')
    def validate_amount(self, key: str, value: float) -> float:
        """Validate amount is positive.

        Args:
            key: The field name.
            value: The amount value.

        Returns:
            The validated amount.
        """
        if value is None or value <= 0:
            raise ValueError("Amount must be a positive number")
        return value

    @validates('payment_method')
    def validate_payment_method(self, key: str, value: str) -> str:
        """Validate payment method is one of the allowed values.

        Args:
            key: The field name.
            value: The payment method value.

        Returns:
            The validated payment method.
        """
        if value not in self.VALID_METHODS:
            raise ValueError(f"Payment method must be one of {self.VALID_METHODS}")
        return value

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

    @validates('card_last_four')
    def validate_card_last_four(self, key: str, value: str | None) -> str | None:
        """Validate card_last_four is exactly 4 digits if provided.

        Args:
            key: The field name.
            value: The card last four digits.

        Returns:
            The validated card last four value.
        """
        if value is not None:
            if not isinstance(value, str) or len(value) != 4 or not value.isdigit():
                raise ValueError("Card last four must be exactly 4 digits")
        return value

    def __repr__(self) -> str:
        return f'<Payment {self.id}, Cart: {self.cart_id}, Status: {self.status}, Amount: {self.amount}>'

    def to_dict(self) -> dict:
        """Serialize the payment to a dictionary with camelCase keys.

        Returns:
            Dictionary representation of the payment.
        """
        return {
            'id': self.id,
            'cartId': self.cart_id,
            'amount': self.amount,
            'paymentMethod': self.payment_method,
            'cardLastFour': self.card_last_four,
            'status': self.status,
            'transactionId': self.transaction_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
