# app/utils/formatters.py

import datetime


def format_expiry(expiry):
    """
    Convert expiry YYYY-MM-DD → DD-MMM-YYYY
    Example: 2025-02-27 → 27-FEB-2025
    """
    y, m, d = expiry.split("-")
    months = [
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
        "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
    ]
    return f"{d}-{months[int(m) - 1]}-{y}"


def format_date_to_dd_mm_yyyy(ts):

    dt = datetime.datetime.strptime(ts, "%d-%b-%Y")
    return dt.strftime("%d-%m-%Y")


def to_millions(value):
    try:
        return round(float(value) / 1_000_000, 2)
    except:
        return 0
