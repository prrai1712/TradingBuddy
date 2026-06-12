async function loadFullChain() {
  const symbol = document.getElementById("symbol").value;
  const expiry = document.getElementById("expiry").value;

  const url = `/full_chain?symbol=${symbol}&expiry=${expiry}`;
  const res = await safeFetch(url);

  // NSE returns: { data: { data: [...] } }
  if (res && res.data && res.data.data) {
    return res.data;
  }

  return { data: [] };
}
