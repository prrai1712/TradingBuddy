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

    # Convert expiry YYYY-MM-DD → DD-Mmm-YYYY (title cased)
    try:
        expiry_final = format_expiry(expiry).title()
    except Exception:
        expiry_final = "25-Jun-2026"

    is_index = symbol.upper() in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "NIFTYIT"]
    symbol_type = "Indices" if is_index else "Equities"

    url = f"https://www.nseindia.com/api/option-chain-v3?type={symbol_type}&symbol={symbol.upper()}&expiry={expiry_final}"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
        "referer": "https://www.nseindia.com/option-chain",
        "cache-control": "no-cache",
        "pragma": "no-cache",
    }

    data_list = []
    underlying_value = 0
    timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

    try:
        session = requests.Session()
        session.get("https://www.nseindia.com/option-chain", headers=headers, timeout=5)
        resp = session.get(url, headers=headers, timeout=5)
        
        if resp.status_code == 200:
            resp_data = resp.json()
            raw_records = resp_data.get("records", {})
            underlying_value = raw_records.get("underlyingValue", 0)
            timestamp = raw_records.get("timestamp", timestamp)
            raw_data = raw_records.get("data", [])

            for it in raw_data:
                strike = it.get("strikePrice")
                if strike is None:
                    continue
                strike = int(strike)

                ce = it.get("CE", {})
                pe = it.get("PE", {})

                def map_option_fields(opt):
                    if not opt:
                        return {}
                    return {
                        "underlyingValue": opt.get("underlyingValue", underlying_value),
                        "openInterest": opt.get("openInterest", 0),
                        "changeinOpenInterest": opt.get("changeinOpenInterest", 0),
                        "changeinOI": opt.get("changeinOpenInterest", 0),
                        "pchangeinOpenInterest": opt.get("pchangeinOpenInterest", 0),
                        "pchgopeninterest": opt.get("pchangeinOpenInterest", 0),
                        "totalTradedVolume": opt.get("totalTradedVolume", 0),
                        "lastPrice": opt.get("lastPrice", 0),
                        "pChange": opt.get("pChange", 0),
                        "change": opt.get("change", 0),
                        "impliedVolatility": opt.get("impliedVolatility", 0),
                        "totalBuyQuantity": opt.get("totalBuyQuantity", 0),
                        "totalSellQuantity": opt.get("totalSellQuantity", 0),
                    }

                data_list.append({
                    "strikePrice": strike,
                    "CE": map_option_fields(ce),
                    "PE": map_option_fields(pe),
                })
        else:
            print(f"Failed to fetch option chain, status: {resp.status_code}")
    except Exception as e:
        print(f"Error fetching option chain: {e}")

    # Sort strikes ascending
    data_list.sort(key=lambda x: x["strikePrice"])

    return {
        "records": {
            "strikeData": data_list,
            "underlyingValue": underlying_value,
            "expiryDates": [expiry_final],
            "timestamp": timestamp
        },
        "filtered": {
            "data": data_list
        },
        "data": data_list
    }
