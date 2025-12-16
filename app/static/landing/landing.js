const lineCtx = document.getElementById("lineChart");
const barCtx = document.getElementById("barChart");

const commonOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { display: false },
    y: { display: false }
  }
};

// LINE CHART
new Chart(lineCtx, {
  type: "line",
  data: {
    labels: Array.from({ length: 20 }, (_, i) => i),
    datasets: [{
      data: [10,12,11,15,18,16,20,22,21,25,27,26,30,32,31,34,36,35,38,40],
      borderColor: "#3d7cff",
      tension: 0.4,
      pointRadius: 0
    }]
  },
  options: commonOptions
});

// BAR CHART
new Chart(barCtx, {
  type: "bar",
  data: {
    labels: ["CE","PE","CE","PE","CE"],
    datasets: [{
      data: [40, 28, 50, 32, 45],
      backgroundColor: "#0b69ff"
    }]
  },
  options: commonOptions
});

// BUTTON NAVIGATION
document.getElementById("enterBtn").addEventListener("click", () => {
  window.location.href = "/dashboard";
});
