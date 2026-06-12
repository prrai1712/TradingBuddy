// charts.js
export let combinedChart = null;
export let niftyChart = null;

export function renderCombinedChart(canvasId, labels, ce, pe, theme) {
    if (combinedChart) combinedChart.destroy();

    combinedChart = new Chart(document.getElementById(canvasId), {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "CE Close",
                    data: ce,
                    borderColor: "#4a8af4",
                    pointBackgroundColor: "#4a8af4",
                    tension: 0.25
                },
                {
                    label: "PE Close",
                    data: pe,
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
}

export function renderNiftyChart(canvasId, labels, prices, theme) {
    if (niftyChart) niftyChart.destroy();

    niftyChart = new Chart(document.getElementById(canvasId), {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "Spot Close",
                    data: prices,
                    borderColor: "#4caf50",
                    pointBackgroundColor: "#4caf50",
                    tension: 0.25
                }
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
}
