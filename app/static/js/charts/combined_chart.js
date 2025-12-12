function drawCombinedChart(labels, cePrices, pePrices, theme) {
    return new Chart(document.getElementById("combinedChart"), {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "CE Close",
                    data: cePrices,
                    borderColor: "#4a8af4",
                    tension: 0.25
                },
                {
                    label: "PE Close",
                    data: pePrices,
                    borderColor: "#ff4e4e",
                    tension: 0.25
                }
            ]
        },
        options: {
            plugins: {
                legend: { labels: { color: theme.text } },
                tooltip: {
                    backgroundColor: theme.tooltipBg,
                    titleColor: theme.text,
                    bodyColor: theme.text
                }
            },
            scales: {
                x: { ticks: { color: theme.text }, grid: { color: theme.grid }},
                y: { ticks: { color: theme.text }, grid: { color: theme.grid }}
            }
        }
    });
}
