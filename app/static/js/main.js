// main.js - app entry (module)
import { getPrice } from "./loadData.js";
import { loadYears, loadExpiryDates, autoDates, resetControls } from "./ui.js";
import { rebuildChartTheme } from "./theme.js";
import { combinedChart, niftyChart } from "./charts.js";
import { isDarkMode } from "./theme.js";

// Expose functions used from HTML (buttons / selects)
window.getPrice = getPrice;
window.resetControls = resetControls;
window.autoDates = autoDates;
window.loadExpiryDates = loadExpiryDates;

window.addEventListener("DOMContentLoaded", () => {
    // Load UI defaults
    loadYears();
    loadExpiryDates();

    // Theme init
    const themeToggle = document.getElementById("themeToggle");
    if (!themeToggle) return;

    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        themeToggle.textContent = "☀️";
    } else {
        themeToggle.textContent = "🌙";
    }

    themeToggle.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");

        if (document.body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
            themeToggle.textContent = "☀️";
        } else {
            localStorage.setItem("theme", "light");
            themeToggle.textContent = "🌙";
        }

        // update chart theme only (no refetch)
        if (combinedChart) rebuildChartTheme(combinedChart);
        if (niftyChart) rebuildChartTheme(niftyChart);
    });
});
