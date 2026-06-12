import requests
from datetime import datetime, timedelta
from app.utils.formatters import format_expiry

def fetch_unblocked_option_chain(symbol: str, expiry: str = None) -> dict:
    if not expiry:
        # Fetch active expiry dates for current year to get a default
        current_year = str(datetime.now().year)
        url = f"https://www.nseindia.com/api/historicalOR/meta/foCPV/expireDts?instrument=OPTIDX&symbol={symbol}&year={current_year}"
        headers = {
            "user-agent": "Mozilla/5.0",
            "referer": "https://www.nseindia.com/",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            dates = resp.json().get("expiresDts", [])
            if dates:
                exp_raw = dates[0] # e.g. "02-JAN-2025"
                d, mmm, y = exp_raw.split("-")
                months = [
                    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
                ]
                m = str(months.index(mmm.upper()) + 1).zfill(2)
                expiry = f"{y}-{m}-{d}"
            else:
                expiry = "2026-06-25"
        except:
            expiry = "2026-06-25"

    # Convert expiry YYYY-MM-DD → DD-MMM-YYYY
    try:
        expiry_final = format_expiry(expiry)
        y = expiry.split("-")[0]
    except:
        expiry_final = "25-JUN-2026"
        y = "2026"

    # Query foCPV for the expiry date to get all strikes
    expiry_dt = datetime.strptime(expiry if expiry else "2026-06-25", "%Y-%m-%d")
    today_dt = datetime.now()

    if expiry_dt.date() < today_dt.date():
        query_date = expiry_dt.strftime("%d-%m-%Y")
    else:
        query_date = today_dt.strftime("%d-%m-%Y")

    url = "https://www.nseindia.com/api/historicalOR/foCPV"
    params = {
        "from": query_date,
        "to": query_date,
        "instrumentType": "OPTIDX",
        "symbol": symbol,
        "year": y,
        "expiryDate": expiry_final,
    }
    headers = {
        "user-agent": "Mozilla/5.0",
        "referer": "https://www.nseindia.com/",
    }

    rows = []
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        data = resp.json()
        rows = data.get("data", [])
        
        # If the query_date returned nothing (e.g. holiday or weekend),
        # query the last 7 days to find the latest active trading day!
        if not rows:
            from_date_str = (expiry_dt - timedelta(days=7) if expiry_dt.date() < today_dt.date() else today_dt - timedelta(days=7)).strftime("%d-%m-%Y")
            params["from"] = from_date_str
            resp = requests.get(url, params=params, headers=headers, timeout=5)
            rows = resp.json().get("data", [])
    except Exception as e:
        print(f"Error fetching option chain: {e}")
        rows = []

    # If rows contains multiple days, filter to get only the most recent day's data
    if rows:
        latest_date = rows[0].get("FH_TIMESTAMP")
        rows = [r for r in rows if r.get("FH_TIMESTAMP") == latest_date]

    # Group by strike price
    strikes_dict = {}
    underlying_value = 0

    for it in rows:
        strike = it.get("FH_STRIKE_PRICE")
        if strike is None:
            continue
        strike = int(strike)
        
        opt_type = it.get("FH_OPTION_TYPE")
        if opt_type not in ["CE", "PE"]:
            continue
            
        underlying = it.get("FH_UNDERLYING_VALUE")
        if underlying:
            underlying_value = underlying
            
        if strike not in strikes_dict:
            strikes_dict[strike] = {
                "strikePrice": strike,
                "CE": {},
                "PE": {}
            }
            
        # Map fields to match standard option chain response
        strikes_dict[strike][opt_type] = {
            "underlyingValue": underlying,
            "openInterest": it.get("FH_OPEN_INT"),
            "changeinOpenInterest": it.get("FH_CHANGE_IN_OI"),
            "totalTradedVolume": it.get("FH_TOT_TRADED_QTY"),
            "lastPrice": it.get("FH_LAST_TRADED_PRICE"),
            "pChange": it.get("FH_CHANGE_IN_OI"),
            "pchgopeninterest": 0,
            "impliedVolatility": 0
        }

    # Sort strikes ascending
    sorted_strikes = sorted(strikes_dict.keys())
    data_list = [strikes_dict[s] for s in sorted_strikes]

    return {
        "records": {
            "strikeData": data_list,
            "underlyingValue": underlying_value,
            "expiryDates": [expiry_final]
        },
        "filtered": {
            "data": data_list
        },
        "data": data_list
    }
