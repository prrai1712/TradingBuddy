async function loadExpiryDates() {
    const symbol = document.getElementById("symbol").value;
    const year = document.getElementById("year").value;

    try {
        const res = await fetch(`/expiry_dates?symbol=${symbol}&year=${year}`);
        const list = await res.json();

        const drop = document.getElementById("expiry");
        drop.innerHTML = "";

        const mmMap = {
            JAN: "01", FEB: "02", MAR: "03", APR: "04", MAY: "05", JUN: "06",
            JUL: "07", AUG: "08", SEP: "09", OCT: "10", NOV: "11", DEC: "12"
        };

        list.forEach(exp => {
            const [d, mmm, y] = exp.split("-");
            const mm = mmMap[mmm];
            drop.innerHTML += `<option value="${y}-${mm}-${d}">${exp}</option>`;
        });

        autoDates();
    } catch (err) {
        document.getElementById("result").innerText = "Failed to load expiry dates";
    }
}
