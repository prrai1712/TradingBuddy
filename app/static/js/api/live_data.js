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

async function loadMarketStatus() {
    try {
        const response = await fetch("/market_status");
        if (!response.ok) return;
        const data = await response.json();

        // 1. Find NIFTY 50 from marketState
        const states = data.marketState || [];
        const niftyState = states.find(s => s.index === "NIFTY 50");

        if (niftyState) {
            const niftyPrice = niftyState.last;
            const niftyChange = niftyState.percentChange;
            const sign = niftyChange >= 0 ? "▲" : "▼";
            const color = niftyChange >= 0 ? "#34d399" : "#f87171";

            // Update liveNiftyBadge in header
            const niftyBadge = document.getElementById("liveNiftyBadge");
            if (niftyBadge) {
                niftyBadge.innerHTML = `NIFTY: <b>${niftyPrice}</b> <span style="font-size:12px; margin-left:5px; color:${color}">${sign} ${Math.abs(niftyChange).toFixed(2)}%</span>`;
            }

            // Also update niftyLive text in Dashboard if it exists
            const niftyLive = document.getElementById("niftyLive");
            if (niftyLive) {
                niftyLive.innerHTML = `NIFTY Spot (Live): <b>${niftyPrice}</b> <span style="margin-left:8px; color:${color}">${sign} ${Math.abs(niftyChange).toFixed(2)}%</span>`;
            }
        }

        // 2. Update Market Status Dot and Text
        const capMarket = states.find(s => s.market === "Capital Market");
        if (capMarket) {
            const status = capMarket.marketStatus; // "Open" or "Closed"
            const statusMessage = capMarket.marketStatusMessage || "";
            const marketStatusText = document.querySelector(".market-status");

            if (marketStatusText) {
                marketStatusText.innerHTML = `<span class="status-dot"></span> ${status}`;
                const statusDot = marketStatusText.querySelector(".status-dot");
                if (statusDot) {
                    if (status.toLowerCase() === "open") {
                        statusDot.style.backgroundColor = "var(--success)";
                    } else {
                        statusDot.style.backgroundColor = "var(--danger)";
                    }
                }
                marketStatusText.title = statusMessage;
            }
        }

        // 3. Add GIFT NIFTY badge
        const giftNifty = data.giftnifty;
        if (giftNifty) {
            let giftBadge = document.getElementById("giftNiftyBadge");
            if (!giftBadge) {
                giftBadge = document.createElement("div");
                giftBadge.id = "giftNiftyBadge";
                giftBadge.className = "live-nifty-badge";
                giftBadge.style.background = "linear-gradient(135deg, #6366f1, #4f46e5)"; // nice indigo color
                giftBadge.style.marginLeft = "10px";
                const niftyBadge = document.getElementById("liveNiftyBadge");
                if (niftyBadge) {
                    niftyBadge.parentNode.insertBefore(giftBadge, niftyBadge.nextSibling);
                }
            }

            if (giftBadge) {
                const giftPrice = giftNifty.LASTPRICE;
                const giftChange = giftNifty.PERCHANGE;
                const sign = giftChange >= 0 ? "▲" : "▼";
                const color = giftChange >= 0 ? "#34d399" : "#f87171";
                giftBadge.innerHTML = `GIFT NIFTY: <b>${giftPrice}</b> <span style="font-size:12px; margin-left:5px; color:${color}">${sign} ${Math.abs(giftChange).toFixed(2)}%</span>`;
            }
        }
    } catch (error) {
        console.error("Error loading market status:", error);
    }
}

// Expose to window
window.loadMarketStatus = loadMarketStatus;

