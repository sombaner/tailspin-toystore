from flask import jsonify, request, Response, Blueprint
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
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
    """Get all games, optionally filtered by a search query.

    Args:
        None

    Query Parameters:
        search: Optional query parameter to filter games by title.

    Returns:
        JSON list of games matching the search criteria, or all games if no search query.
    """
    # Use the base query for all games
    games_query = get_games_base_query()

    # Apply search filter if provided
    search = request.args.get('search', '').strip()
    if search:
        games_query = games_query.filter(Game.title.ilike('%' + search + '%'))

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
