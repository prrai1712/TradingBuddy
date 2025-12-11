from flask import Blueprint, request, jsonify
import requests
import datetime

nifty_bp = Blueprint("nifty", __name__)


@nifty_bp.get("/nifty_spot")
def nifty_spot():
    symbol = request.args.get("symbol", "NIFTY")
    fromDate = request.args.get("fromDate")
    toDate = request.args.get("toDate")

    if not fromDate or not toDate:
        return jsonify({"error": "Missing date range"}), 400

    names = {
        "NIFTY": "NIFTY 50",
        "BANKNIFTY": "NIFTY BANK",
    }
    index_name = names.get(symbol.upper(), "NIFTY 50")

    # Convert DD-MM-YYYY → DD-MM-YYYY (same format)
    f_d, f_m, f_y = fromDate.split("-")
    t_d, t_m, t_y = toDate.split("-")

    nse_from = f"{f_d}-{f_m}-{f_y}"
    nse_to = f"{t_d}-{t_m}-{t_y}"

    session = requests.Session()
    headers = {
        "user-agent": "Mozilla/5.0",
        "referer": "https://www.nseindia.com/",
    }

    # Warm-up request
    session.get("https://www.nseindia.com", headers=headers)

    url = (
        "https://www.nseindia.com/api/historical/indicesHistory"
        f"?indexType={index_name.replace(' ', '%20')}"
        f"&from={nse_from}&to={nse_to}"
    )

    resp = session.get(url, headers=headers)

    try:
        rows = resp.json().get("data", {}).get("indexCloseOnlineRecords", [])
    except:
        rows = []

    output = []
    for it in rows:
        ts = it.get("EOD_TIMESTAMP")
        close = it.get("EOD_CLOSE_INDEX_VAL")
        if not ts or close is None:
            continue

        dt = datetime.datetime.strptime(ts, "%d-%b-%Y")
        output.append({
            "date": dt.strftime("%d-%m-%Y"),
            "close": close
        })

    return jsonify(output)
