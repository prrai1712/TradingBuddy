async function loadLiveData() {
    const symbol = document.getElementById("symbol").value;
    const expiry = document.getElementById("expiry").value;
    const strike = document.getElementById("strike").value;

    if (!strike) return;

    const url = new URL("/live_option_data", window.location.origin);
    url.search = new URLSearchParams({ symbol, expiry, strike });

    const res = await fetch(url);
    const data = await res.json();

    document.getElementById("ceTitle").textContent = `${strike} CE`;
    document.getElementById("peTitle").textContent = `${strike} PE`;

    document.getElementById("niftyLive").innerHTML =
        `NIFTY Spot (Live): <b>${data.nifty_spot}</b>`;

    const CE = data.CE;
    const PE = data.PE;

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
