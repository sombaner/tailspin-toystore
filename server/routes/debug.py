from __future__ import annotations

from flask import Blueprint, jsonify, request, Response
from typing import List, Tuple
import gc

# A module-level bucket to intentionally retain memory between requests
_LEAK_BUCKET: List[bytearray] = []

debug_bp = Blueprint('debug', __name__)


def _total_bytes() -> int:
    return sum(len(chunk) for chunk in _LEAK_BUCKET)


@debug_bp.route('/api/debug/leak', methods=['POST', 'GET'])
def induce_leak() -> Tuple[Response, int] | Response:
    """
    Induce a controlled memory leak by allocating and retaining bytearrays in a module-level bucket.

    Query/body params:
    - mb: megabytes per allocation (default: 1)
    - count: number of allocations to retain (default: 1)

    Returns current stats (chunks and totalBytes).
    """
    try:
        # Support both query string and form body
        mb_str = request.args.get('mb') or request.form.get('mb') or '1'
        count_str = request.args.get('count') or request.form.get('count') or '1'
        mb = int(mb_str)
        count = int(count_str)
        if mb <= 0 or count <= 0:
            raise ValueError('mb and count must be positive integers')
    except Exception as ex:
        return jsonify({
            'error': 'invalid_parameters',
            'message': f'{ex}'
        }), 400

    bytes_per = mb * 1024 * 1024
    for _ in range(count):
        # Allocate and retain
        _LEAK_BUCKET.append(bytearray(bytes_per))

    return jsonify({
        'status': 'ok',
        'chunks': len(_LEAK_BUCKET),
        'totalBytes': _total_bytes()
    })


@debug_bp.route('/api/debug/leak/stats', methods=['GET'])
def leak_stats() -> Response:
    return jsonify({
        'chunks': len(_LEAK_BUCKET),
        'totalBytes': _total_bytes()
    })


@debug_bp.route('/api/debug/leak/clear', methods=['POST'])
def leak_clear() -> Response:
    _LEAK_BUCKET.clear()
    gc.collect()
    return jsonify({
        'status': 'cleared',
        'chunks': len(_LEAK_BUCKET),
        'totalBytes': _total_bytes()
    })
