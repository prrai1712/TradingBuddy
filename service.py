from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import datetime

app = Flask(__name__)
CORS(app)

# ------------------------------------------
#  EXPIRY DATES API  (Year + Symbol based)
# ------------------------------------------
@app.get("/expiry_dates")
def expiry_dates():
    symbol = request.args.get("symbol", "NIFTY")
    year = request.args.get("year", "2025")

    url = f"https://www.nseindia.com/api/historicalOR/meta/foCPV/expireDts?instrument=OPTIDX&symbol={symbol}&year={year}"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh)",
        "accept": "*/*",
        "referer": "https://www.nseindia.com/"
    }

    res = requests.get(url, headers=headers)
    try:
        data = res.json()
    except:
        return jsonify([])

    return jsonify(data.get("expiresDts", []))



# ------------------------------------------
#  OPEN PRICE API (Main Data)
# ------------------------------------------
@app.get("/open_price")
def open_price():

    symbol = request.args.get("symbol")
    expiry = request.args.get("expiry")         
    optionType = request.args.get("optionType")
    strike = request.args.get("strike")
    fromDate = request.args.get("fromDate")     
    toDate = request.args.get("toDate")         
    
    if not all([symbol, expiry, optionType, strike, fromDate, toDate]):
        return jsonify({"error": "Missing parameters"}), 400

    # Convert expiry yyyy-mm-dd → DD-MMM-YYYY
    y, m, d = expiry.split("-")
    months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
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
        "strikePrice": strike
    }

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh)",
        "accept": "*/*",
        "referer": "https://www.nseindia.com/"
    }

    res = requests.get(url, params=params, headers=headers)

    try:
        data = res.json()
    except:
        return jsonify({"error": "Invalid NSE response"}), 500

    if "data" not in data or len(data["data"]) == 0:
        return jsonify({"error": "No data found"}), 404

    final_output = []
    for item in data["data"]:
        final_output.append({
            "market price": item.get("FH_UNDERLYING_VALUE"),
            "open": item.get("FH_OPENING_PRICE"),
            "close" : item.get("FH_CLOSING_PRICE"),
            "date": item.get("FH_TIMESTAMP")
        })

    return jsonify(final_output)



# ===========================================================
#  NEW API → NIFTY / BANKNIFTY SPOT CLOSING PRICE (Yahoo)
# ===========================================================

def to_unix(date_str):
    d = datetime.datetime.strptime(date_str, "%d-%m-%Y")
    return int(time.mktime(d.timetuple()))


@app.get("/nifty_spot")
def nifty_spot():
    import requests
    import datetime
    from flask import jsonify, request

    symbol = request.args.get("symbol", "NIFTY")
    fromDate = request.args.get("fromDate")  
    toDate = request.args.get("toDate")     

    if not fromDate or not toDate:
        return jsonify({"error": "Missing date range"}), 400

    symbol_map = {
        "NIFTY": "NIFTY 50",
        "BANKNIFTY": "NIFTY BANK"
    }

    index_name = symbol_map.get(symbol.upper(), "NIFTY 50")

    f_d, f_m, f_y = fromDate.split("-")
    t_d, t_m, t_y = toDate.split("-")

    nse_from = f"{f_d}-{f_m}-{f_y}"
    nse_to = f"{t_d}-{t_m}-{t_y}"

    session = requests.Session()

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "accept": "*/*",
        "referer": "https://www.nseindia.com/reports-indices-historical-index-data"
    }

    session.get("https://www.nseindia.com", headers=headers)

    url = (
        "https://www.nseindia.com/api/historical/indicesHistory"
        f"?indexType={index_name.replace(' ', '%20')}"
        f"&from={nse_from}&to={nse_to}"
    )

    res = session.get(url, headers=headers)

    try:
        data = res.json()
    except:
        return jsonify({"error": "Invalid NSE response"}), 500

    rows = data.get("data", [])
    if not rows:
        return jsonify({"error": "No data found"}), 404

    output = []
    data = rows.get("indexCloseOnlineRecords")
    for item in data:
        ts = item.get("EOD_TIMESTAMP")
        close = item.get("EOD_CLOSE_INDEX_VAL")

        if not ts or close is None:
            continue

        dt = datetime.datetime.strptime(ts, "%d-%b-%Y")
        final_date = dt.strftime("%d-%m-%Y")

        output.append({
            "date": final_date,
            "close": close
        })

    return jsonify(output)



# ------------------------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)
