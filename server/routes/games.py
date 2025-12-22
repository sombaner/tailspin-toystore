from flask import jsonify, Response, Blueprint, g
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query
from utils.logging_config import get_logger

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

# Get logger for this module
logger = get_logger(__name__)

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
    try:
        # Use the base query for all games
        games_query = get_games_base_query().all()
        
        # Log successful query
        logger.info(f"Retrieved {len(games_query)} games", extra={
            'correlation_id': getattr(g, 'correlation_id', None),
            'game_count': len(games_query)
        })
        
        # Convert the results using the model's to_dict method
        games_list = [game.to_dict() for game in games_query]
        
        return jsonify(games_list)
    except Exception as e:
        logger.error(f"Error retrieving games: {str(e)}", extra={
            'correlation_id': getattr(g, 'correlation_id', None),
            'error_type': type(e).__name__
        }, exc_info=True)
        return jsonify({"error": "Failed to retrieve games"}), 500

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    try:
        # Use the base query and add filter for specific game
        game_query = get_games_base_query().filter(Game.id == id).first()
        
        # Return 404 if game not found
        if not game_query:
            logger.warning(f"Game not found: {id}", extra={
                'correlation_id': getattr(g, 'correlation_id', None),
                'game_id': id
            })
            return jsonify({"error": "Game not found"}), 404
        
        # Log successful retrieval
        logger.info(f"Retrieved game: {game_query.title}", extra={
            'correlation_id': getattr(g, 'correlation_id', None),
            'game_id': id,
            'game_title': game_query.title
        })
        
        # Convert the result using the model's to_dict method
        game = game_query.to_dict()
        
        return jsonify(game)
    except Exception as e:
        logger.error(f"Error retrieving game {id}: {str(e)}", extra={
            'correlation_id': getattr(g, 'correlation_id', None),
            'game_id': id,
            'error_type': type(e).__name__
        }, exc_info=True)
        return jsonify({"error": "Failed to retrieve game"}), 500
