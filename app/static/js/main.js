/* ===============================
   APP INITIALIZATION
=============================== */
function initApp() {
    // Load presets
    loadYears();
    loadExpiryDates();

    // Load initial market status
    if (window.loadMarketStatus) {
        window.loadMarketStatus();
    }

    // Load initial trading signal and market sentiment
    setTimeout(() => {
        fetchTradingSignal();
        fetchMarketSentiment();
    }, 1000);

    // expose functions to window for inline HTML handlers
    window.getPrice = getPrice;
    window.resetControls = resetControls;
}

/* ===============================
   START INITIALIZATION
=============================== */
window.onload = initApp;
