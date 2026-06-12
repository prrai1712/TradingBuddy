from flask import Blueprint, request, jsonify
import requests
from datetime import datetime, timedelta

live_bp = Blueprint("live_data", __name__)


@live_bp.get("/live_option_data")
def live_option_data():
    symbol = request.args.get("symbol")
    expiry = request.args.get("expiry")
    strike = request.args.get("strike")

    if not (symbol and expiry and strike):
        return jsonify({"error": "Missing parameters"}), 400

    try:
        # Parse expiry date
        expiry_dt = datetime.strptime(expiry, "%Y-%m-%d")
        today_dt = datetime.now()

        # Date range selection: 7 days is enough to ensure we get a trading day
        if expiry_dt.date() < today_dt.date():
            # Already expired: take 7 days leading up to expiry date
            to_date_dt = expiry_dt
            from_date_dt = expiry_dt - timedelta(days=7)
        else:
            # Active/Future contract: take last 7 days leading up to today
            to_date_dt = today_dt
            from_date_dt = today_dt - timedelta(days=7)

        from_date_str = from_date_dt.strftime("%d-%m-%Y")
        to_date_str = to_date_dt.strftime("%d-%m-%Y")

        y = expiry_dt.strftime("%Y")
        m = expiry_dt.strftime("%m")
        d = expiry_dt.strftime("%d")

        months = [
            "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
            "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
        ]
        expiry_final = f"{d}-{months[int(m)-1]}-{y}"

        results = {}

        url = "https://www.nseindia.com/api/historicalOR/foCPV"
        headers = {
            "user-agent": "Mozilla/5.0",
            "referer": "https://www.nseindia.com/",
        }

        for opt in ["CE", "PE"]:
            params = {
                "from": from_date_str,
                "to": to_date_str,
                "instrumentType": "OPTIDX",
                "symbol": symbol,
                "year": y,
                "expiryDate": expiry_final,
                "optionType": opt,
                "strikePrice": strike,
            }

            resp = requests.get(url, params=params, headers=headers, timeout=5)
            data = resp.json()
            rows = data.get("data", [])

            if not rows:
                results[opt] = {"error": "No data available in the selected range"}
                continue

            # rows are returned in reverse chronological order (newest first).
            # We take the first element (index 0) as the latest available data point.
            latest = rows[0]

            results[opt] = {
                "ltp": latest.get("FH_LAST_TRADED_PRICE"),
                "open": latest.get("FH_OPENING_PRICE"),
                "high": latest.get("FH_TRADE_HIGH_PRICE"),
                "low": latest.get("FH_TRADE_LOW_PRICE"),
                "oi": latest.get("FH_OPEN_INT"),
                "oi_change": latest.get("FH_CHANGE_IN_OI"),
                "traded_value": latest.get("FH_TOT_TRADED_VAL"),
                "underlying": latest.get("FH_UNDERLYING_VALUE"),
                "last_update": latest.get("FH_TIMESTAMP"),
            }

        # Nifty Spot from CE record
        try:
            results["nifty_spot"] = results["CE"].get("underlying")
        except:
            results["nifty_spot"] = None

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
