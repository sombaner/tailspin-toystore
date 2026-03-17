from flask import jsonify, request, Response, Blueprint
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

# Valid sort options mapping to SQLAlchemy order_by clauses
SORT_OPTIONS: dict[str, list] = {
    'popularity': [Game.popularity.desc()],
    'rating': [Game.star_rating.desc()],
    'release_date': [Game.release_date.desc()],
    'title': [Game.title.asc()],
}

def get_games_base_query() -> Query:
    """Build the base query for retrieving games with publisher and category joins.

    Returns:
        SQLAlchemy Query with outer joins on Publisher and Category.
    """
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    """Get all games, optionally filtered by search and sorted.

    Args:
        None

    Query Parameters:
        search: Optional query parameter to filter games by title.
        sort: Optional sort order. One of 'popularity', 'rating', 'release_date', 'title'.

    Returns:
        JSON list of games matching the criteria.
    """
    games_query = get_games_base_query()

    # Apply search filter if provided
    search = request.args.get('search', '').strip()
    if search:
        games_query = games_query.filter(Game.title.ilike('%' + search + '%'))

    # Apply sorting
    sort = request.args.get('sort', '').strip()
    if sort in SORT_OPTIONS:
        games_query = games_query.order_by(*SORT_OPTIONS[sort])
    else:
        games_query = games_query.order_by(Game.title.asc())

    games_list = [game.to_dict() for game in games_query.all()]
    
    return jsonify(games_list)

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)
