function drawGauge(score) {
    const canvas = document.getElementById("sentimentGauge");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const cx = canvas.width / 2;
    const cy = canvas.height - 10;
    const radius = 90;

    // Draw background track (gradient from red -> yellow -> green)
    const gradient = ctx.createLinearGradient(cx - radius, 0, cx + radius, 0);
    gradient.addColorStop(0, "#ef4444");  // Red
    gradient.addColorStop(0.5, "#fbbf24");  // Yellow
    gradient.addColorStop(1, "#10b981");  // Green

    ctx.beginPath();
    ctx.lineWidth = 16;
    ctx.lineCap = "round";
    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
    ctx.arc(cx, cy, radius, Math.PI, 0);
    ctx.stroke();

    ctx.beginPath();
    ctx.strokeStyle = gradient;
    ctx.arc(cx, cy, radius, Math.PI, 0);
    ctx.stroke();

    // Map score (-1 to +1) to angle (Math.PI to 0)
    // -1 is PI (left, Red), 0 is PI/2 (top, Yellow), +1 is 0 (right, Green)
    const angle = Math.PI - ((score + 1) / 2 * Math.PI);

    // Draw needle shadow
    ctx.shadowColor = "rgba(0, 0, 0, 0.4)";
    ctx.shadowBlur = 6;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 2;

    // Draw Needle
    ctx.beginPath();
    ctx.lineWidth = 4;
    ctx.strokeStyle = document.body.classList.contains("dark-mode") ? "#e8e8e8" : "#1f1f1f";
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + Math.cos(angle) * (radius - 5), cy - Math.sin(angle) * (radius - 5));
    ctx.stroke();

    // Reset shadow
    ctx.shadowBlur = 0;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;

    // Draw center pivot
    ctx.beginPath();
    ctx.arc(cx, cy, 8, 0, Math.PI * 2);
    ctx.fillStyle = document.body.classList.contains("dark-mode") ? "#e8e8e8" : "#1f1f1f";
    ctx.fill();

    ctx.beginPath();
    ctx.arc(cx, cy, 4, 0, Math.PI * 2);
    ctx.fillStyle = "#3d7cff";
    ctx.fill();
}
