// theme.js
export function isDarkMode() {
    return document.body.classList.contains("dark-mode");
}

export function getChartTheme() {
    if (isDarkMode()) {
        return {
            grid: "rgba(255,255,255,0.09)",
            text: "#e8e8e8",
            background: "#1a1c25",
            tooltipBg: "#2b238",
        };
    }
    return {
        grid: "rgba(0,0,0,0.1)",
        text: "#333",
        background: "#ffffff",
        tooltipBg: "#f4f4f4",
    };
}

// Update Chart.js instance theme (no data refetch)
export function rebuildChartTheme(chart) {
    const theme = getChartTheme();

    if (!chart || !chart.options) return;

    if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
        chart.options.plugins.legend.labels.color = theme.text;
    }
    if (chart.options.plugins && chart.options.plugins.tooltip) {
        chart.options.plugins.tooltip.backgroundColor = theme.tooltipBg;
        chart.options.plugins.tooltip.titleColor = theme.text;
        chart.options.plugins.tooltip.bodyColor = theme.text;
    }

    if (chart.options.scales && chart.options.scales.x) {
        if (!chart.options.scales.x.ticks) chart.options.scales.x.ticks = {};
        chart.options.scales.x.ticks.color = theme.text;
        if (!chart.options.scales.x.grid) chart.options.scales.x.grid = {};
        chart.options.scales.x.grid.color = theme.grid;
    }
    if (chart.options.scales && chart.options.scales.y) {
        if (!chart.options.scales.y.ticks) chart.options.scales.y.ticks = {};
        chart.options.scales.y.ticks.color = theme.text;
        if (!chart.options.scales.y.grid) chart.options.scales.y.grid = {};
        chart.options.scales.y.grid.color = theme.grid;
    }

    chart.update();
}
