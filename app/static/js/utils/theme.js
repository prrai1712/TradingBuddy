function isDarkMode() {
    return document.body.classList.contains("dark-mode");
}

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

// theme toggle logic stays same
document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("themeToggle");

    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        themeToggle.textContent = "☀️";
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

        if (window.combinedChart || window.niftyChart) {
            getPrice();
        }
    });
});
