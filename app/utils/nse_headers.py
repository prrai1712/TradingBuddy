# app/utils/nse_headers.py

def get_nse_headers(user_agent=None):
    """
    Returns NSE-safe headers for API requests.
    User-Agent is customizable from browser request headers.
    """

    default_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    return {
        "user-agent": user_agent or default_agent,
        "accept": "*/*",
        "referer": "https://www.nseindia.com/",
        "accept-language": "en-US,en;q=0.9",
    }
