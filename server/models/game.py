from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Game(BaseModel):
    """Represents a game available for crowdfunding on the platform."""

    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    star_rating = db.Column(db.Float, nullable=True)
    popularity = db.Column(db.Integer, nullable=True, default=0)
    release_date = db.Column(db.Date, nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    
    # Foreign keys for one-to-many relationships
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'), nullable=False)
    
    # One-to-many relationships (many games belong to one category/publisher)
    category = relationship("Category", back_populates="games")
    publisher = relationship("Publisher", back_populates="games")
    reviews = relationship("Review", back_populates="game", lazy='dynamic')
    
    @validates('title')
    def validate_name(self, key, name):
        return self.validate_string_length('Game title', name, min_length=2)
    
    @validates('description')
    def validate_description(self, key, description):
        if description is not None:
            return self.validate_string_length('Description', description, min_length=10, allow_none=True)
        return description
    
    def __repr__(self):
        return f'<Game {self.title}, ID: {self.id}>'

    def to_dict(self):
        """Serialize the game to a dictionary with camelCase keys.

        Returns:
            Dictionary representation of the game.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'publisher': {'id': self.publisher.id, 'name': self.publisher.name} if self.publisher else None,
            'category': {'id': self.category.id, 'name': self.category.name} if self.category else None,
            'starRating': self.star_rating,
            'popularity': self.popularity,
            'releaseDate': self.release_date.isoformat() if self.release_date else None,
            'price': self.price,
        }