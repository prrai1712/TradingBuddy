# app/routes/full_chain.py
from flask import Blueprint, request, jsonify
from app.utils.option_chain_helper import fetch_unblocked_option_chain

full_chain_bp = Blueprint("full_chain", __name__)


@full_chain_bp.get("/full_chain")
def full_chain():
    symbol = request.args.get("symbol", "NIFTY").upper()
    expiry = request.args.get("expiry")

    try:
        data = fetch_unblocked_option_chain(symbol, expiry)
        return jsonify({"ok": True, "data": data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
