from flask import jsonify, request, Response, Blueprint
from models import db, Cart, CartItem, Game

cart_bp = Blueprint('cart', __name__)


def get_or_create_cart(session_id: str) -> Cart:
    """Get an active cart for the session, or create one if none exists.

    Args:
        session_id: The browser session identifier.

    Returns:
        The active Cart instance for this session.
    """
    cart = db.session.query(Cart).filter_by(
        session_id=session_id, status='active'
    ).first()
    if not cart:
        cart = Cart(session_id=session_id)
        db.session.add(cart)
        db.session.commit()
    return cart


@cart_bp.route('/api/cart', methods=['GET'])
def get_cart() -> tuple[Response, int] | Response:
    """Get or create a cart for the given session.

    Query Parameters:
        session_id: Required session identifier.

    Returns:
        JSON representation of the cart with its items.
    """
    session_id = request.args.get('session_id', '').strip()
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    cart = get_or_create_cart(session_id)
    return jsonify(cart.to_dict())


@cart_bp.route('/api/cart/items', methods=['POST'])
def add_item() -> tuple[Response, int] | Response:
    """Add an item to the cart. If the item already exists, increment quantity.

    Request Body:
        sessionId: The browser session identifier.
        gameId: The ID of the game to add.
        quantity: Number of units to add (default 1).

    Returns:
        JSON representation of the updated cart, or an error.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    session_id = data.get('sessionId', '')
    game_id = data.get('gameId')
    quantity = data.get('quantity', 1)

    if not session_id:
        return jsonify({"error": "sessionId is required"}), 400
    if not game_id:
        return jsonify({"error": "gameId is required"}), 400
    if not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "quantity must be a positive integer"}), 400

    game = db.session.query(Game).get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    cart = get_or_create_cart(session_id)

    existing_item = db.session.query(CartItem).filter_by(
        cart_id=cart.id, game_id=game_id
    ).first()

    if existing_item:
        existing_item.quantity = existing_item.quantity + quantity
        db.session.commit()
    else:
        item = CartItem(
            cart_id=cart.id,
            game_id=game_id,
            quantity=quantity,
            price=game.price if game.price else 0.0,
        )
        db.session.add(item)
        db.session.commit()

    return jsonify(cart.to_dict()), 201


@cart_bp.route('/api/cart/items/<int:item_id>', methods=['PUT'])
def update_item(item_id: int) -> tuple[Response, int] | Response:
    """Update item quantity. If quantity is 0, remove the item.

    Args:
        item_id: The cart item ID.

    Request Body:
        quantity: New quantity value.

    Returns:
        JSON representation of the updated cart, or an error.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    quantity = data.get('quantity')
    if quantity is None or not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "quantity must be a non-negative integer"}), 400

    item = db.session.query(CartItem).get(item_id)
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    cart = db.session.query(Cart).get(item.cart_id)

    if quantity == 0:
        db.session.delete(item)
        db.session.commit()
    else:
        item.quantity = quantity
        db.session.commit()

    return jsonify(cart.to_dict())


@cart_bp.route('/api/cart/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id: int) -> tuple[Response, int] | Response:
    """Remove an item from the cart.

    Args:
        item_id: The cart item ID to remove.

    Returns:
        JSON representation of the updated cart, or an error.
    """
    item = db.session.query(CartItem).get(item_id)
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    cart = db.session.query(Cart).get(item.cart_id)
    db.session.delete(item)
    db.session.commit()

    return jsonify(cart.to_dict())


@cart_bp.route('/api/cart/count', methods=['GET'])
def get_cart_count() -> tuple[Response, int] | Response:
    """Get the total item count in the cart for badge display.

    Query Parameters:
        session_id: Required session identifier.

    Returns:
        JSON with the total count of items in the cart.
    """
    session_id = request.args.get('session_id', '').strip()
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    cart = db.session.query(Cart).filter_by(
        session_id=session_id, status='active'
    ).first()

    if not cart:
        return jsonify({"count": 0})

    total = db.session.query(db.func.coalesce(
        db.func.sum(CartItem.quantity), 0
    )).filter_by(cart_id=cart.id).scalar()

    return jsonify({"count": int(total)})
