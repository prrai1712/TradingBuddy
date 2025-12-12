function drawGauge(score) {
    const canvas = document.getElementById("sentimentGauge");
    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const angle = (score + 1) / 2 * Math.PI;

    // Background arc
    ctx.beginPath();
    ctx.lineWidth = 14;
    ctx.strokeStyle = "#777";
    ctx.arc(130, 150, 100, Math.PI, 0);
    ctx.stroke();

    // Indicator needle
    ctx.beginPath();
    ctx.lineWidth = 6;
    ctx.strokeStyle = score >= 0 ? "lime" : "red";
    ctx.moveTo(130, 150);
    ctx.lineTo(130 - Math.cos(angle) * 95, 150 - Math.sin(angle) * 95);
    ctx.stroke();
}
