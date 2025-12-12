async function fetchNiftySpot(symbol, fromDate, toDate) {
    const url = new URL("/nifty_spot", window.location.origin);
    url.search = new URLSearchParams({ symbol, fromDate, toDate });
    return safeFetch(url);
}
