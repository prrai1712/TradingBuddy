function loadYears() {
    const y = document.getElementById("year");
    y.innerHTML = "";
    const thisYear = new Date().getFullYear();
    for (let i = 2015; i <= thisYear + 1; i++) {
        const o = document.createElement("option");
        o.value = i;
        o.textContent = i;
        y.appendChild(o);
    }
    y.value = thisYear;
}

function fmtDate(d) {
    return `${String(d.getDate()).padStart(2, "0")}-${String(d.getMonth() + 1).padStart(2, "0")}-${d.getFullYear()}`;
}

function autoDates() {
    const expiry = document.getElementById("expiry").value;
    if (!expiry) return;
    const e = new Date(expiry);
    const from = new Date(e);
    from.setDate(from.getDate() - 30);
    document.getElementById("fromDate").value = fmtDate(from);
    document.getElementById("toDate").value = fmtDate(e);
}

function resetControls() {
    loadYears();
    loadExpiryDates();
    document.getElementById("strike").value = "";
    document.getElementById("result").innerText = "";
}
