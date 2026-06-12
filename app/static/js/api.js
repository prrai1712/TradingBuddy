// api.js
export function buildCEURL(params) {
    const url = new URL("/open_price", window.location.origin);
    url.search = new URLSearchParams({ ...params, optionType: "CE" });
    return url;
}

export function buildPEURL(params) {
    const url = new URL("/open_price", window.location.origin);
    url.search = new URLSearchParams({ ...params, optionType: "PE" });
    return url;
}

export function buildNiftyURL(symbol, fromDate, toDate) {
    const url = new URL("/nifty_spot", window.location.origin);
    url.search = new URLSearchParams({ symbol, fromDate, toDate });
    return url;
}

export function buildLiveDataURL(symbol, expiry, strike) {
    const url = new URL("/live_option_data", window.location.origin);
    url.search = new URLSearchParams({ symbol, expiry, strike });
    return url;
}
