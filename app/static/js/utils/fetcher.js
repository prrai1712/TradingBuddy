async function safeFetch(url) {
    const r = await fetch(url);
    let data;
    try { data = await r.json(); }
    catch { data = { error: "Invalid JSON" }; }
    if (!r.ok) return { error: data || `HTTP ${r.status}` };
    return data;
}
