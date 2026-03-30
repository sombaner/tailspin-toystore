from datetime import datetime, timezone
from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship


class Review(BaseModel):
    """Represents a user review for a game."""

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    reviewer_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Foreign key
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    # Relationship
    game = relationship("Game", back_populates="reviews")

    @validates('rating')
    def validate_rating(self, key, rating):
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValueError("Rating must be an integer between 1 and 5")
        return rating

    @validates('reviewer_name')
    def validate_reviewer_name(self, key, name):
        return self.validate_string_length('Reviewer name', name, min_length=2)

    @validates('review_text')
    def validate_review_text(self, key, text):
        return self.validate_string_length('Review text', text, min_length=10)

    def __repr__(self):
        return f'<Review {self.id} for Game {self.game_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'gameId': self.game_id,
            'rating': self.rating,
            'reviewText': self.review_text,
            'reviewerName': self.reviewer_name,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
