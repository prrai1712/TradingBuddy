function renderChainTable(chain) {
  const container = document.getElementById("chainContainer");

  // Extract correct array
  const rows = chain?.data?.data;

  if (!rows || !Array.isArray(rows) || rows.length === 0) {
    container.innerHTML = "<p>No chain data</p>";
    return;
  }

  const spot = rows[0]?.CE?.underlyingValue || 0;

  const atmStrike = rows.reduce((prev, curr) =>
    Math.abs(curr.strikePrice - spot) < Math.abs(prev.strikePrice - spot)
      ? curr
      : prev
  ).strikePrice;

  let html = `
    <table class="chain-table">
      <thead>
        <tr>
          <th colspan="4" class="ce-head">CALLS</th>
          <th class="strike-head">Strike</th>
          <th colspan="4" class="pe-head">PUTS</th>
        </tr>
        <tr>
          <th>OI</th>
          <th>Chg OI</th>
          <th>Vol</th>
          <th>LTP</th>
          <th>Strike</th>
          <th>LTP</th>
          <th>Vol</th>
          <th>Chg OI</th>
          <th>OI</th>
        </tr>
      </thead>
      <tbody>
  `;

  rows.forEach(row => {
    const CE = row.CE || {};
    const PE = row.PE || {};
    const strike = row.strikePrice;

    const isATM = strike === atmStrike;

    html += `
      <tr class="${isATM ? "atm-row" : ""}">
        <td>${CE.openInterest ?? "-"}</td>
        <td>${CE.changeinOpenInterest ?? "-"}</td>
        <td>${CE.totalTradedVolume ?? "-"}</td>
        <td>${CE.lastPrice ?? "-"}</td>

        <td class="strike-cell">${strike}</td>

        <td>${PE.lastPrice ?? "-"}</td>
        <td>${PE.totalTradedVolume ?? "-"}</td>
        <td>${PE.changeinOpenInterest ?? "-"}</td>
        <td>${PE.openInterest ?? "-"}</td>
      </tr>
    `;
  });

  html += "</tbody></table>";

  container.innerHTML = html;
}
