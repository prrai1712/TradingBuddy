from flask import Blueprint, request, jsonify
import requests

live_bp = Blueprint("live_data", __name__)


@live_bp.get("/live_option_data")
def live_option_data():
    symbol = request.args.get("symbol")
    expiry = request.args.get("expiry")
    strike = request.args.get("strike")

    if not (symbol and expiry and strike):
        return jsonify({"error": "Missing parameters"}), 400

    yyyy, mm, dd = expiry.split("-")
    strike_fmt = f"{float(strike):.2f}"

    results = {}

    for opt in ["CE", "PE"]:
        identifier = f"OPTIDX{symbol}{dd}-{mm}-{yyyy}{opt}{strike_fmt}"

        url = (
            "https://www.nseindia.com/api/NextApi/apiClient/GetQuoteApi"
            f"?functionName=getTradeInfoDerivative&symbol={symbol}"
            f"&identifier={identifier}&type=W"
        )

        headers = {
            "user-agent": request.headers.get(
                "User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            ),
            "accept": "*/*",
            "referer": "https://www.nseindia.com/get-quote/derivatives",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=5)
            data = resp.json()
            d = data["derivateResponse"][0]

            results[opt] = {
                "ltp": d["metaData"]["last"],
                "open": d["metaData"]["open"],
                "high": d["metaData"]["high"],
                "low": d["metaData"]["low"],
                "oi": d["tradeInfo"]["openinterest"],
                "oi_change": d["tradeInfo"]["chngopeninterest"],
                "traded_value": d["tradeInfo"]["totalTradedValue"],
                "underlying": d["tradeInfo"]["underlyingvalue"],
                "last_update": d["lastUpdateTime"],
            }

        except Exception as e:
            results[opt] = {"error": str(e)}

    # Nifty Spot from CE record
    try:
        results["nifty_spot"] = results["CE"].get("underlying")
    except:
        results["nifty_spot"] = None

    return jsonify(results)
