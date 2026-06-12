async function loadLiveData() {
    const symbol = document.getElementById("symbol").value;
    const expiry = document.getElementById("expiry").value;
    const strike = document.getElementById("strike").value;

    if (!strike) return;

    const url = new URL("/live_option_data", window.location.origin);
    url.search = new URLSearchParams({ symbol, expiry, strike });

    const res = await fetch(url);
    const data = await res.json();

    // Add strike to data for UI updates
    data.strike = strike;

    // Update header NIFTY live badge
    const headerNifty = document.getElementById("headerNiftyLive");
    if (headerNifty && data.nifty_spot) {
        headerNifty.textContent = `NIFTY: ${data.nifty_spot}`;
    }

    document.getElementById("ceTitle").textContent = `${strike} CE`;
    document.getElementById("peTitle").textContent = `${strike} PE`;

    document.getElementById("niftyLive").innerHTML =
        `NIFTY Spot (Live): <b>${data.nifty_spot}</b>`;

    const CE = data.CE;
    const PE = data.PE;

    function format(d) {
        const total_money_value = (Number(d.traded_value) / 1_000_000).toFixed(2);
        return `
        <p><span>LTP:</span> <b>${d.ltp}</b></p>
        <p><span>Open:</span> <span>${d.open}</span></p>
        <p><span>High:</span> <span>${d.high}</span></p>
        <p><span>Low:</span> <span>${d.low}</span></p>
        <p><span>OI:</span> <span>${d.oi}</span></p>
        <p><span>OI Change:</span> <span>${d.oi_change}</span></p>
        <p><span>Turnover:</span> <span>${total_money_value}M</span></p>
        <p><small style="color: var(--text-light);">Updated: ${d.last_update}</small></p>
      `;
    }

    document.getElementById("ceBox").innerHTML = format(CE);
    document.getElementById("peBox").innerHTML = format(PE);

    const oi_ratio = (PE.oi / CE.oi).toFixed(2);
    const value_ratio = (PE.traded_value / CE.traded_value).toFixed(2);
    const premium_ratio = (PE.ltp / CE.ltp).toFixed(2);

    document.getElementById("ratioBox").innerHTML = `
      <p><span>OI Ratio (PE/CE):</span> <b>${oi_ratio}</b></p>
      <p><span>Value Ratio (PE/CE):</span> <b>${value_ratio}</b></p>
      <p><span>Premium Ratio (PE/CE):</span> <b>${premium_ratio}</b></p>
    `;
    
    // Fetch and update PCR analysis
    fetchPCRAnalysisForLive(symbol, expiry);
}

async function fetchPCRAnalysisForLive(symbol, expiry) {
    try {
        const url = new URL("/pcr_analysis", window.location.origin);
        url.search = new URLSearchParams({ symbol, expiry });
        const response = await safeFetch(url);
        
        if (response.success) {
            updatePCRBox(response);
        }
    } catch (error) {
        console.error('Error fetching PCR for live data:', error);
    }
}
