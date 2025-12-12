function drawNiftyChart(spotData, theme) {
    return new Chart(document.getElementById("niftyChart"), {
        type: "line",
        data: {
            labels: spotData.map(x => x.date),
            datasets: [
                {
                    label: "Spot Close",
                    data: spotData.map(x => x.close),
                    borderColor: "#4caf50",
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
