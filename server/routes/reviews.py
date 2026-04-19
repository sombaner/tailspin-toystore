from flask import jsonify, request, Response, Blueprint
from models import db, Game, Review

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/api/games/<int:game_id>/reviews', methods=['GET'])
def get_reviews(game_id: int) -> tuple[Response, int] | Response:
    """Get all reviews for a game."""
    game = db.session.query(Game).get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    reviews = (
        db.session.query(Review)
        .filter(Review.game_id == game_id)
        .order_by(Review.created_at.desc())
        .all()
    )

    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    return jsonify({
        'reviews': [r.to_dict() for r in reviews],
        'averageRating': avg_rating,
        'totalReviews': len(reviews),
    })


@reviews_bp.route('/api/games/<int:game_id>/reviews', methods=['POST'])
def create_review(game_id: int) -> tuple[Response, int]:
    """Create a new review for a game."""
    game = db.session.query(Game).get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    rating = data.get('rating')
    review_text = data.get('reviewText', '').strip()
    reviewer_name = data.get('reviewerName', '').strip()

    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
    if len(reviewer_name) < 2:
        return jsonify({"error": "Reviewer name must be at least 2 characters"}), 400
    if len(review_text) < 10:
        return jsonify({"error": "Review text must be at least 10 characters"}), 400

    try:
        review = Review(
            game_id=game_id,
            rating=rating,
            review_text=review_text,
            reviewer_name=reviewer_name,
        )
        db.session.add(review)

        # Update the game's star_rating to the new average
        all_reviews = (
            db.session.query(Review)
            .filter(Review.game_id == game_id)
            .all()
        )
        all_ratings = [r.rating for r in all_reviews] + [rating]
        game.star_rating = round(sum(all_ratings) / len(all_ratings), 1)

        db.session.commit()
        return jsonify(review.to_dict()), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
