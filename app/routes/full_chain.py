# app/routes/full_chain.py
from flask import Blueprint, request, jsonify
import requests
from app.utils.nse_headers import get_nse_headers

full_chain_bp = Blueprint("full_chain", __name__)

@full_chain_bp.get("/full_chain")
def full_chain():
    symbol = request.args.get("symbol", "NIFTY").upper()
    expiry = request.args.get("expiry")

    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    if expiry:
        url += f"&expiryDate={expiry}"

    headers = get_nse_headers(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    headers["referer"] = "https://www.nseindia.com/option-chain"
    headers["accept"] = "application/json"

    try:
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.headers.get("Content-Type", "").startswith("text/html"):
            return jsonify({
                "ok": False,
                "error": "Blocked by NSE (HTML returned)",
                "snippet": resp.text[:200]
            }), 502

        return jsonify({"ok": True, "data": resp.json()})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
