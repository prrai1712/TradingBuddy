from flask import Blueprint, request, jsonify
import requests
import datetime

nifty_bp = Blueprint("nifty", __name__)


@nifty_bp.get("/nifty_spot")
def nifty_spot():
    symbol = request.args.get("symbol", "NIFTY")
    expiry = request.args.get("expiry")
    strike = request.args.get("strike")
    fromDate = request.args.get("fromDate")
    toDate = request.args.get("toDate")

    if not all([symbol, expiry, strike, fromDate, toDate]):
        return jsonify({"error": "Missing params"}), 400

    # Convert expiry YYYY-MM-DD → DD-MMM-YYYY
    try:
        y, m, d = expiry.split("-")
        months = [
            "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
            "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
        ]
        expiry_final = f"{d}-{months[int(m)-1]}-{y}"
    except:
        return jsonify({"error": "Invalid expiry format"}), 400

    url = "https://www.nseindia.com/api/historicalOR/foCPV"

    params = {
        "from": fromDate,
        "to": toDate,
        "instrumentType": "OPTIDX",
        "symbol": symbol,
        "year": y,
        "expiryDate": expiry_final,
        "optionType": "CE",
        "strikePrice": strike,
    }

    headers = {
        "user-agent": "Mozilla/5.0",
        "referer": "https://www.nseindia.com/",
    }

    try:
        resp = requests.get(url, params=params, headers=headers)
        rows = resp.json().get("data", [])
    except Exception as e:
        import sys
        print(f"Error fetching nifty spot: {e}", file=sys.stderr)
        rows = []

    output = []
    for it in rows:
        val = it.get("FH_UNDERLYING_VALUE")
        ts = it.get("FH_TIMESTAMP")
        if val is None or not ts:
            continue
        output.append({
            "date": ts,
            "close": val
        })

    # Reverse to return chronological order (oldest first)
    output.reverse()
    return jsonify(output)
