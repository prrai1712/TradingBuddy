from flask import Blueprint, request, jsonify
import requests

expiry_bp = Blueprint("expiry", __name__)


@expiry_bp.get("/expiry_dates")
def expiry_dates():
    symbol = request.args.get("symbol", "NIFTY")
    year = request.args.get("year", "2025")

    url = (
        "https://www.nseindia.com/api/historicalOR/meta/foCPV/expireDts"
        f"?instrument=OPTIDX&symbol={symbol}&year={year}"
    )

    headers = {
        "user-agent": "Mozilla/5.0",
        "referer": "https://www.nseindia.com/",
    }

    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        return jsonify(data.get("expiresDts", []))
    except:
        return jsonify([])
