/* ===============================
   APP INITIALIZATION
=============================== */
function initApp() {
    // Theme toggle init
    const themeToggle = document.getElementById("themeToggle");
    if (themeToggle) {
        if (localStorage.getItem("theme") === "dark") {
            document.body.classList.add("dark-mode");
            themeToggle.textContent = "☀️ Light Mode";
        } else {
            themeToggle.textContent = "🌙 Dark Mode";
        }

        themeToggle.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            if (document.body.classList.contains("dark-mode")) {
                localStorage.setItem("theme", "dark");
                themeToggle.textContent = "☀️ Light Mode";
            } else {
                localStorage.setItem("theme", "light");
                themeToggle.textContent = "🌙 Dark Mode";
            }
            
            // update chart themes if active
            const theme = getChartTheme();
            if (window.combinedChart) {
                window.combinedChart.options.plugins.legend.labels.color = theme.text;
                window.combinedChart.options.plugins.tooltip.backgroundColor = theme.tooltipBg;
                window.combinedChart.options.plugins.tooltip.titleColor = theme.text;
                window.combinedChart.options.plugins.tooltip.bodyColor = theme.text;
                window.combinedChart.options.scales.x.ticks.color = theme.text;
                window.combinedChart.options.scales.x.grid.color = theme.grid;
                window.combinedChart.options.scales.y.ticks.color = theme.text;
                window.combinedChart.options.scales.y.grid.color = theme.grid;
                window.combinedChart.update();
            }
            if (window.niftyChart) {
                window.niftyChart.options.plugins.legend.labels.color = theme.text;
                window.niftyChart.options.plugins.tooltip.backgroundColor = theme.tooltipBg;
                window.niftyChart.options.plugins.tooltip.titleColor = theme.text;
                window.niftyChart.options.plugins.tooltip.bodyColor = theme.text;
                window.niftyChart.options.scales.x.ticks.color = theme.text;
                window.niftyChart.options.scales.x.grid.color = theme.grid;
                window.niftyChart.options.scales.y.ticks.color = theme.text;
                window.niftyChart.options.scales.y.grid.color = theme.grid;
                window.niftyChart.update();
            }
        });
    }

    // Load presets
    loadYears();
    loadExpiryDates();

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
