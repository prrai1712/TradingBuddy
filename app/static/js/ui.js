// ui.js
import { fmtDate, safeFetch } from "./helpers.js";

export function loadYears() {
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

export async function loadExpiryDates() {
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
            const formatted = `${y}-${mm}-${d}`;
            const opt = document.createElement("option");
            opt.value = formatted;
            opt.textContent = exp;
            drop.appendChild(opt);
        });

        autoDates();
    } catch (err) {
        document.getElementById("result").innerText = "Failed to load expiry dates";
    }
}

export function autoDates() {
    const expiry = document.getElementById("expiry").value;
    if (!expiry) return;
    const e = new Date(expiry);
    const from = new Date(e);
    from.setDate(from.getDate() - 30);
    document.getElementById("fromDate").value = fmtDate(from);
    document.getElementById("toDate").value = fmtDate(e);
}

export function resetControls() {
    loadYears();
    loadExpiryDates();
    document.getElementById("strike").value = "";
    document.getElementById("result").innerText = "";
    document.getElementById("ceBox").innerHTML = "--";
    document.getElementById("peBox").innerHTML = "--";
    document.getElementById("ratioBox").innerHTML = "--";
}
