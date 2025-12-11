from flask import Blueprint, request, jsonify
import requests

option_bp = Blueprint("option_price", __name__)


@option_bp.get("/open_price")
def open_price():
    symbol = request.args.get("symbol")
    expiry = request.args.get("expiry")
    optionType = request.args.get("optionType")
    strike = request.args.get("strike")
    fromDate = request.args.get("fromDate")
    toDate = request.args.get("toDate")

    if not all([symbol, expiry, optionType, strike, fromDate, toDate]):
        return jsonify({"error": "Missing params"}), 400

    # Convert expiry YYYY-MM-DD → DD-MMM-YYYY
    y, m, d = expiry.split("-")
    months = [
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
        "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
    ]
    expiry_final = f"{d}-{months[int(m)-1]}-{y}"

    url = "https://www.nseindia.com/api/historicalOR/foCPV"

    params = {
        "from": fromDate,
        "to": toDate,
        "instrumentType": "OPTIDX",
        "symbol": symbol,
        "year": y,
        "expiryDate": expiry_final,
        "optionType": optionType,
        "strikePrice": strike,
    }

    headers = {
        "user-agent": "Mozilla/5.0",
        "referer": "https://www.nseindia.com/",
    }

    resp = requests.get(url, params=params, headers=headers)

    # Parse & return required fields
    try:
        rows = resp.json().get("data", [])
    except:
        rows = []

    output = []
    for it in rows:
        output.append({
            "open": it.get("FH_OPENING_PRICE"),
            "close": it.get("FH_CLOSING_PRICE"),
            "date": it.get("FH_TIMESTAMP")
        })

    return jsonify(output)
