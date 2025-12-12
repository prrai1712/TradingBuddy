let combinedChart = null;
let niftyChart = null;

async function getPrice() {
    document.getElementById("result").innerText = "Loading...";

    const baseParams = {
        symbol: document.getElementById("symbol").value,
        expiry: document.getElementById("expiry").value,
        strike: document.getElementById("strike").value,
        fromDate: document.getElementById("fromDate").value,
        toDate: document.getElementById("toDate").value,
    };

    if (!baseParams.fromDate || !baseParams.toDate) {
        document.getElementById("result").innerText = "Enter date range";
        return;
    }

    try {
        const ceURL = new URL("/open_price", window.location.origin);
        ceURL.search = new URLSearchParams({ ...baseParams, optionType: "CE" });

        const peURL = new URL("/open_price", window.location.origin);
        peURL.search = new URLSearchParams({ ...baseParams, optionType: "PE" });

        const [ceResp, peResp] = await Promise.all([safeFetch(ceURL), safeFetch(peURL)]);

        if (ceResp.error || peResp.error) {
            document.getElementById("result").innerText = "Failed loading CE/PE";
            return;
        }

        const ceData = Array.isArray(ceResp) ? ceResp : [];
        const peData = Array.isArray(peResp) ? peResp : [];

        let labels = ceData.length ? ceData.map(x => x.date).reverse() :
            peData.map(x => x.date).reverse();

        const cePrices = ceData.map(x => x.close).reverse();
        const pePrices = peData.map(x => x.close).reverse();

        const theme = getChartTheme();

        if (combinedChart) combinedChart.destroy();
        combinedChart = drawCombinedChart(labels, cePrices, pePrices, theme);

        // NIFTY spot
        const nsURL = new URL("/nifty_spot", window.location.origin);
        nsURL.search = new URLSearchParams({
            symbol: baseParams.symbol,
            fromDate: baseParams.fromDate,
            toDate: baseParams.toDate,
        });

        const spotResp = await safeFetch(nsURL);
        const spotData = Array.isArray(spotResp) ? spotResp : [];

        const theme2 = getChartTheme();

        if (niftyChart) niftyChart.destroy();
        niftyChart = drawNiftyChart(spotData, theme2);

        document.getElementById("result").innerText = "Charts Loaded ✔";

    } catch (err) {
        document.getElementById("result").innerText = "Unexpected error";
    }

    await loadLiveData();

    const fullChain = await loadFullChain();
    renderChainTable(fullChain);

    const sentiment = await computeSentiment(fullChain);
    renderSentimentUI(sentiment);

    drawGauge(sentiment.finalScore);
}
