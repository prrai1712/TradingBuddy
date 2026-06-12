// helpers.js
export function fmtDate(d) {
    return `${String(d.getDate()).padStart(2,"0")}-${String(d.getMonth()+1).padStart(2,"0")}-${d.getFullYear()}`;
}

export async function safeFetch(url) {
    const r = await fetch(url);
    let data;
    try { data = await r.json(); }
    catch { data = { error: "Invalid JSON" }; }
    if (!r.ok) return { error: data || `HTTP ${r.status}` };
    return data;
}
