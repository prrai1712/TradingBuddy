// loadData.js
import { safeFetch } from "./helpers.js";
import { getChartTheme } from "./theme.js";
import { renderCombinedChart, renderNiftyChart } from "./charts.js";
import { buildCEURL, buildPEURL, buildNiftyURL, buildLiveDataURL } from "./api.js";

/* ---------------------------------------
   MAIN PRICE LOAD
----------------------------------------*/
export async function getPrice() {
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
        const ceURL = buildCEURL(baseParams);
        const peURL = buildPEURL(baseParams);

        const [ceResp, peResp] = await Promise.all([
            safeFetch(ceURL),
            safeFetch(peURL)
        ]);

        if (ceResp.error || peResp.error) {
            document.getElementById("result").innerText = "Failed loading CE/PE";
            return;
        }

        const ceData = Array.isArray(ceResp) ? ceResp : [];
        const peData = Array.isArray(peResp) ? peResp : [];

        let labels = ceData.length ? ceData.map(x => x.date).reverse() : peData.map(x => x.date).reverse();

        const cePrices = ceData.map(x => x.close).reverse();
        const pePrices = peData.map(x => x.close).reverse();

        const theme = getChartTheme();
        renderCombinedChart("combinedChart", labels, cePrices, pePrices, theme);

        // NIFTY Chart
        const niftyURL = buildNiftyURL(baseParams.symbol, baseParams.fromDate, baseParams.toDate);
        const spotResp = await safeFetch(niftyURL);
        const spotData = Array.isArray(spotResp) ? spotResp : [];

        const theme2 = getChartTheme();
        renderNiftyChart("niftyChart", spotData.map(x => x.date), spotData.map(x => x.close), theme2);

        document.getElementById("result").innerText = "Charts Loaded ✔";

    } catch (err) {
        document.getElementById("result").innerText = "Unexpected error";
    }

    // load live data after charts
    await loadLiveData();
}

/* ---------------------------------------
   LIVE OPTION DATA
----------------------------------------*/
export async function loadLiveData() {
    const symbol = document.getElementById("symbol").value;
    const expiry = document.getElementById("expiry").value;
    const strike = document.getElementById("strike").value;

    if (!strike) {
        document.getElementById("ceTitle").textContent = "-- CE";
        document.getElementById("peTitle").textContent = "-- PE";
        document.getElementById("ceBox").innerHTML = "--";
        document.getElementById("peBox").innerHTML = "--";
        document.getElementById("ratioBox").innerHTML = "--";
        return;
    }

    // show loading ONLY when API called
    document.getElementById("ceBox").innerHTML = "<p>Loading...</p>";
    document.getElementById("peBox").innerHTML = "<p>Loading...</p>";
    document.getElementById("ratioBox").innerHTML = "<p>Loading...</p>";

    const url = buildLiveDataURL(symbol, expiry, strike);
    const res = await safeFetch(url);

    if (!res || res.error) {
        document.getElementById("ceBox").innerHTML = "--";
        document.getElementById("peBox").innerHTML = "--";
        document.getElementById("ratioBox").innerHTML = "--";
        return;
    }

    document.getElementById("ceTitle").textContent = `${strike} CE`;
    document.getElementById("peTitle").textContent = `${strike} PE`;

    document.getElementById("niftyLive").innerHTML = `NIFTY Spot (Live): <b>${res.nifty_spot}</b>`;

    const CE = res.CE;
    const PE = res.PE;

    function format(d) {
        const total_money_value = (Number(d.traded_value) / 1_000_000).toFixed(2);
        return `
      <p>LTP: <b>${d.ltp}</b></p>
      <p>Open: ${d.open}</p>
      <p>High: ${d.high}</p>
      <p>Low: ${d.low}</p>
      <p>OI: ${d.oi}</p>
      <p>OI Change: ${d.oi_change}</p>
      <p>Total Money Value: ${total_money_value}M</p>
      <p><small>Updated: ${d.last_update}</small></p>
    `;
    }

    document.getElementById("ceBox").innerHTML = format(CE);
    document.getElementById("peBox").innerHTML = format(PE);

    const oi_ratio = (PE.oi / CE.oi).toFixed(2);
    const value_ratio = (PE.traded_value / CE.traded_value).toFixed(2);
    const premium_ratio = (PE.ltp / CE.ltp).toFixed(2);

    document.getElementById("ratioBox").innerHTML = `
    <p><b>OI Ratio (PE/CE):</b> ${oi_ratio}</p>
    <p><b>Value Ratio (PE/CE):</b> ${value_ratio}</p>
    <p><b>Premium Ratio (PE/CE):</b> ${premium_ratio}</p>
  `;
}
