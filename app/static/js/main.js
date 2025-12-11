let combinedChart = null;
let niftyChart = null;

/* ---------------------------------------
   THEME HELPERS
----------------------------------------*/

// Detect dark mode
function isDarkMode() {
    return document.body.classList.contains("dark-mode");
}

// Theme palette for charts
function getChartTheme() {
    if (isDarkMode()) {
        return {
            grid: "rgba(255,255,255,0.09)",
            text: "#e8e8e8",
            background: "#1a1c25",
            tooltipBg: "#2b2e38",
        };
    }
    return {
        grid: "rgba(0,0,0,0.1)",
        text: "#333",
        background: "#ffffff",
        tooltipBg: "#f4f4f4",
    };
}

/* ---------------------------------------
   LOAD YEARS
----------------------------------------*/
function loadYears() {
    const y = document.getElementById("year");
    y.innerHTML = "";
    const thisYear = new Date().getFullYear();
    for (let i = 2015; i <= thisYear + 1; i++) {
        const o = document.createElement("option");
        o.value = i;
        o.textContent = i;
        y.appendChild(o);
    }
    y.value = thisYear;
}

/* ---------------------------------------
   EXPIRY DATES
----------------------------------------*/
async function loadExpiryDates() {
    const symbol = document.getElementById("symbol").value;
    const year = document.getElementById("year").value;

    try {
        const res = await fetch(`/expiry_dates?symbol=${symbol}&year=${year}`);
        const list = await res.json();

        const drop = document.getElementById("expiry");
        drop.innerHTML = "";

        const mmMap = {
            JAN: "01", FEB: "02", MAR: "03", APR: "04", MAY: "05", JUN: "06",
            JUL: "07", AUG: "08", SEP: "09", OCT: "10", NOV: "11", DEC: "12"
        };

        list.forEach(exp => {
            const [d, mmm, y] = exp.split("-");
            const mm = mmMap[mmm];
            const formatted = `${y}-${mm}-${d}`;
            const opt = document.createElement("option");
            opt.value = formatted;
            opt.textContent = exp;
            drop.appendChild(opt);
        });

        autoDates();
    } catch (err) {
        document.getElementById("result").innerText = "Failed to load expiry dates";
    }
}

/* ---------------------------------------
   DATE HELPERS
----------------------------------------*/
function fmtDate(d) {
    return `${String(d.getDate()).padStart(2, "0")}-${String(d.getMonth() + 1).padStart(2, "0")}-${d.getFullYear()}`;
}

function autoDates() {
    const expiry = document.getElementById("expiry").value;
    if (!expiry) return;
    const e = new Date(expiry);
    const from = new Date(e);
    from.setDate(from.getDate() - 30);
    document.getElementById("fromDate").value = fmtDate(from);
    document.getElementById("toDate").value = fmtDate(e);
}

function resetControls() {
    loadYears();
    loadExpiryDates();
    document.getElementById("strike").value = "";
    document.getElementById("result").innerText = "";
}

/* ---------------------------------------
   SAFE FETCH WRAPPER
----------------------------------------*/
async function safeFetch(url) {
    const r = await fetch(url);
    let data;
    try { data = await r.json(); }
    catch { data = { error: "Invalid JSON" }; }
    if (!r.ok) return { error: data || `HTTP ${r.status}` };
    return data;
}

/* ---------------------------------------
   MAIN PRICE LOAD
----------------------------------------*/
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

        // DESTROY OLD CHART
        if (combinedChart) combinedChart.destroy();

        combinedChart = new Chart(document.getElementById("combinedChart"), {
            type: "line",
            data: {
                labels,
                datasets: [
                    {
                        label: "CE Close",
                        data: cePrices,
                        borderColor: "#4a8af4",
                        pointBackgroundColor: "#4a8af4",
                        tension: 0.25
                    },
                    {
                        label: "PE Close",
                        data: pePrices,
                        borderColor: "#ff4e4e",
                        pointBackgroundColor: "#ff4e4e",
                        tension: 0.25
                    },
                ],
            },
            options: {
                plugins: {
                    legend: { labels: { color: theme.text } },
                    tooltip: {
                        backgroundColor: theme.tooltipBg,
                        titleColor: theme.text,
                        bodyColor: theme.text,
                    }
                },
                scales: {
                    x: {
                        ticks: { color: theme.text },
                        grid: { color: theme.grid }
                    },
                    y: {
                        ticks: { color: theme.text },
                        grid: { color: theme.grid }
                    }
                }
            }
        });

        // NIFTY CHART
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

        niftyChart = new Chart(document.getElementById("niftyChart"), {
            type: "line",
            data: {
                labels: spotData.map(x => x.date),
                datasets: [
                    {
                        label: "Spot Close",
                        data: spotData.map(x => x.close),
                        borderColor: "#4caf50",
                        pointBackgroundColor: "#4caf50",
                        tension: 0.25
                    }
                ],
            },
            options: {
                plugins: {
                    legend: { labels: { color: theme2.text } },
                    tooltip: {
                        backgroundColor: theme2.tooltipBg,
                        titleColor: theme2.text,
                        bodyColor: theme2.text,
                    }
                },
                scales: {
                    x: {
                        ticks: { color: theme2.text },
                        grid: { color: theme2.grid }
                    },
                    y: {
                        ticks: { color: theme2.text },
                        grid: { color: theme2.grid }
                    }
                }
            }
        });

        document.getElementById("result").innerText = "Charts Loaded ✔";

    } catch (err) {
        document.getElementById("result").innerText = "Unexpected error";
    }

    await loadLiveData();
}

/* ---------------------------------------
   LIVE OPTION DATA
----------------------------------------*/
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

/* ---------------------------------------
   DARK MODE TOGGLE + CHART REBUILD
----------------------------------------*/
const themeToggle = document.getElementById("themeToggle");

// Load saved theme
if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-mode");
    themeToggle.textContent = "☀️";
}

// Toggle logic
themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");

    if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
        themeToggle.textContent = "☀️";
    } else {
        localStorage.setItem("theme", "light");
        themeToggle.textContent = "🌙";
    }

    // 🔥 Rebuild charts with new theme
    if (combinedChart || niftyChart) {
        getPrice(); // reloads charts with new theme
    }
});

/* ---------------------------------------
   ON PAGE LOAD
----------------------------------------*/
window.onload = function () {
    loadYears();
    loadExpiryDates();
};
