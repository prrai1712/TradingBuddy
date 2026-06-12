// Mini signal chart for hero section

let miniSignalChart = null;

function drawMiniSignalChart(signal, data = []) {
    const ctx = document.getElementById('miniSignalChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (miniSignalChart) {
        miniSignalChart.destroy();
    }
    
    // Get theme colors
    const isDark = document.body.classList.contains('dark-mode');
    const textColor = isDark ? '#e8e8e8' : '#1f1f1f';
    const gridColor = isDark ? '#2f313a' : '#e5e7eb';
    
    // Generate sample data based on signal
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    let chartData = [];
    let borderColor = '#0b69ff';
    
    if (signal === 'CALL') {
        // Upward trend
        chartData = [100, 105, 103, 110, 115];
        borderColor = '#10b981';
    } else if (signal === 'PUT') {
        // Downward trend
        chartData = [100, 95, 97, 90, 85];
        borderColor = '#ef4444';
    } else {
        // Flat/neutral
        chartData = [100, 101, 99, 100, 101];
        borderColor = '#6b7280';
    }
    
    miniSignalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Signal Performance',
                data: chartData,
                borderColor: borderColor,
                backgroundColor: borderColor + '20',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    display: false,
                    grid: {
                        display: false
                    }
                },
                y: {
                    display: false,
                    min: Math.min(...chartData) - 5,
                    max: Math.max(...chartData) + 5,
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

function updateMiniSignalChart(signal) {
    drawMiniSignalChart(signal);
}
