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
        from app.utils.option_chain_helper import fetch_unblocked_option_chain
        # Fetch live option chain data
        chain_data = fetch_unblocked_option_chain(symbol, expiry)
        
        if not chain_data.get("data"):
            return jsonify({"error": "Failed to fetch live option chain data from NSE"}), 502

        nifty_spot = chain_data.get("records", {}).get("underlyingValue", 0)
        last_update = chain_data.get("records", {}).get("timestamp", datetime.now().strftime("%d-%b-%Y %H:%M:%S"))

        # Find the specific strike price in the chain
        strike_val = int(float(strike))
        strike_data = None
        for item in chain_data.get("data", []):
            if int(item.get("strikePrice", 0)) == strike_val:
                strike_data = item
                break

        if not strike_data:
            return jsonify({"error": f"Strike price {strike} not found in option chain"}), 404

        results = {}
        for opt in ["CE", "PE"]:
            opt_data = strike_data.get(opt, {})
            ltp = opt_data.get("lastPrice", 0) or 0
            volume = opt_data.get("totalTradedVolume", 0) or 0
            traded_value = volume * ltp

            results[opt] = {
                "ltp": ltp,
                "open": "-",
                "high": "-",
                "low": "-",
                "oi": opt_data.get("openInterest", 0),
                "oi_change": opt_data.get("changeinOpenInterest", 0),
                "traded_value": traded_value,
                "underlying": nifty_spot,
                "last_update": last_update,
            }

        # Nifty Spot from underlying value
        results["nifty_spot"] = nifty_spot
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@live_bp.get("/market_status")
def market_status():
    url = "https://www.nseindia.com/api/marketStatus"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
        "referer": "https://www.nseindia.com/option-chain",
        "cache-control": "no-cache",
        "pragma": "no-cache",
    }
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com/option-chain", headers=headers, timeout=5)
        resp = session.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify({"error": f"Failed to fetch market status: {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
