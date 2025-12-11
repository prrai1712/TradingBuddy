import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.security import safe_join
from flask_cors import CORS
import requests
import time
import datetime

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


# ---------------- EXPIRY DATES API ----------------
@app.get("/expiry_dates")
def expiry_dates():
    symbol = request.args.get("symbol", "NIFTY")
    year = request.args.get("year", "2025")

    url = f"https://www.nseindia.com/api/historicalOR/meta/foCPV/expireDts?instrument=OPTIDX&symbol={symbol}&year={year}"
    headers = {"user-agent": "Mozilla/5.0", "referer": "https://www.nseindia.com/"}

    resp = requests.get(url, headers=headers)
    try:
        data = resp.json()
        return jsonify(data.get("expiresDts", []))
    except:
        return jsonify([])
    

# ---------------- OPTION CHAIN PRICE FETCH ----------------
@app.get("/open_price")
def open_price():
    symbol = request.args.get("symbol")
    expiry = request.args.get("expiry")
    optionType = request.args.get("optionType")
    strike = request.args.get("strike")
    fromDate = request.args.get("fromDate")
    toDate = request.args.get("toDate")

    if not all([symbol, expiry, optionType, strike, fromDate, toDate]):
        return jsonify({"error": "Missing params"}), 400

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

    headers = {"user-agent": "Mozilla/5.0", "referer": "https://www.nseindia.com/"}

    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()

    output = []
    for item in data.get("data", []):
        output.append({
            "open": item.get("FH_OPENING_PRICE"),
            "close": item.get("FH_CLOSING_PRICE"),
            "date": item.get("FH_TIMESTAMP")
        })

    return jsonify(output)


# ---------------- INDEX SPOT API ----------------
@app.get("/nifty_spot")
def nifty_spot():
    symbol = request.args.get("symbol", "NIFTY")
    fromDate = request.args.get("fromDate")
    toDate = request.args.get("toDate")

    if not fromDate or not toDate:
        return jsonify({"error": "Missing date range"}), 400

    names = {"NIFTY": "NIFTY 50", "BANKNIFTY": "NIFTY BANK"}
    index_name = names.get(symbol.upper(), "NIFTY 50")

    f_d, f_m, f_y = fromDate.split("-")
    t_d, t_m, t_y = toDate.split("-")

    nse_from = f"{f_d}-{f_m}-{f_y}"
    nse_to = f"{t_d}-{t_m}-{t_y}"

    session = requests.Session()
    headers = {"user-agent": "Mozilla/5.0", "referer": "https://www.nseindia.com/"}
    session.get("https://www.nseindia.com", headers=headers)

    url = f"https://www.nseindia.com/api/historical/indicesHistory?indexType={index_name.replace(' ','%20')}&from={nse_from}&to={nse_to}"

    resp = session.get(url, headers=headers)
    data = resp.json()

    rows = data.get("data", {}).get("indexCloseOnlineRecords", [])

    output = []
    for it in rows:
        ts = it.get("EOD_TIMESTAMP")
        close = it.get("EOD_CLOSE_INDEX_VAL")
        if not ts or close is None:
            continue
        dt = datetime.datetime.strptime(ts, "%d-%b-%Y")
        output.append({"date": dt.strftime("%d-%m-%Y"), "close": close})

    return jsonify(output)


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    print("Flask running at http://127.0.0.1:5000/")
    app.run(port=5000, debug=True)
