from flask import jsonify, request, Response, Blueprint
from models import db, Cart, CartItem, Payment

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/api/checkout', methods=['POST'])
def checkout() -> tuple[Response, int] | Response:
    """Process checkout for a cart session.

    Request Body:
        sessionId: The browser session identifier.
        paymentMethod: One of 'credit_card', 'debit_card', 'paypal'.
        cardLastFour: Last four digits of the card (optional, for card payments).

    Returns:
        JSON payment confirmation or an error.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    session_id = data.get('sessionId', '')
    payment_method = data.get('paymentMethod', '')
    card_last_four = data.get('cardLastFour')

    if not session_id:
        return jsonify({"error": "sessionId is required"}), 400
    if not payment_method:
        return jsonify({"error": "paymentMethod is required"}), 400
    if payment_method not in Payment.VALID_METHODS:
        return jsonify({"error": f"paymentMethod must be one of {Payment.VALID_METHODS}"}), 400

    cart = db.session.query(Cart).filter_by(
        session_id=session_id, status='active'
    ).first()
    if not cart:
        return jsonify({"error": "No active cart found for this session"}), 404

    items = cart.items.all()
    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    total = sum(item.price * item.quantity for item in items)
    if total <= 0:
        return jsonify({"error": "Cart total must be greater than zero"}), 400

    payment = Payment(
        cart_id=cart.id,
        amount=round(total, 2),
        payment_method=payment_method,
        card_last_four=card_last_four,
        status='completed',
    )
    db.session.add(payment)

    cart.status = 'checked_out'
    db.session.commit()

    return jsonify(payment.to_dict()), 201


@payments_bp.route('/api/payments/<transaction_id>', methods=['GET'])
def get_payment(transaction_id: str) -> tuple[Response, int] | Response:
    """Get payment status by transaction ID.

    Args:
        transaction_id: The UUID transaction identifier.

    Returns:
        JSON representation of the payment, or a 404 error.
    """
    payment = db.session.query(Payment).filter_by(
        transaction_id=transaction_id
    ).first()

    if not payment:
        return jsonify({"error": "Payment not found"}), 404

    return jsonify(payment.to_dict())
