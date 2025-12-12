/* ===============================
   DYNAMIC MODULE LOADER
=============================== */
function loadScript(path) {
    return new Promise((resolve, reject) => {
        const s = document.createElement("script");
        s.src = path + "?v=4";   // cache-bust
        s.onload = resolve;
        s.onerror = reject;
        document.body.appendChild(s);
    });
}

/* ===============================
   LOAD ALL MODULES
=============================== */
async function loadModules() {
    const files = [
        "/static/js/utils/theme.js",
        "/static/js/utils/dates.js",
        "/static/js/utils/fetcher.js",

        "/static/js/api/expiry.js",
        "/static/js/api/option_price.js",
        "/static/js/api/nifty_spot.js",
        "/static/js/api/live_data.js",
        "/static/js/api/full_chain.js",

        "/static/js/ui/tabs.js",
        "/static/js/ui/option_chain_table.js",
        "/static/js/ui/sentiment.js",
        "/static/js/ui/gauge.js",

        "/static/js/charts/combined_chart.js",
        "/static/js/charts/nifty_chart.js",
    ];

    for (const file of files) {
        await loadScript(file);
    }

    console.log("All modules loaded ✔");

    // Call init after everything is loaded
    initApp();
}

/* ===============================
   APP INITIALIZATION
=============================== */
function initApp() {
    loadYears();
    loadExpiryDates();

    // expose to window for HTML buttons
    window.getPrice = getPrice;
    window.resetControls = resetControls;
}

/* ===============================
   START LOADING MODULES
=============================== */
window.onload = loadModules;
