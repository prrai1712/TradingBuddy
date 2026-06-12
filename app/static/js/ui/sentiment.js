async function computeSentiment(chain) {
    if (!chain || !chain.data) return null;

    const rows = chain.data;

    const spot = rows[0]?.CE?.underlyingValue ?? null;
    if (!spot) return null;

    // Find ATM Strike
    const atmStrike = rows.reduce((prev, curr) =>
        Math.abs(curr.strikePrice - spot) < Math.abs(prev.strikePrice - spot)
            ? curr
            : prev
    );

    const CEatm = atmStrike.CE;
    const PEatm = atmStrike.PE;

    // ---------------------------
    // 1) DOP — Directional OI Pressure
    // ---------------------------
    const dop =
        (PEatm.changeinOpenInterest - CEatm.changeinOpenInterest) /
        (Math.abs(PEatm.changeinOpenInterest) + Math.abs(CEatm.changeinOpenInterest) + 1);

    // ---------------------------
    // 2) SMFI — Smart Money Flow Index
    // ---------------------------
    const ceFlow = CEatm.totalTradedVolume / (CEatm.lastPrice || 1);
    const peFlow = PEatm.totalTradedVolume / (PEatm.lastPrice || 1);
    const smfi = (peFlow - ceFlow) / (peFlow + ceFlow + 1);

    // ---------------------------
    // 3) IV Skew
    // ---------------------------
    const ivSkew = ((PEatm.impliedVolatility || 0) - (CEatm.impliedVolatility || 0)) / 100;

    // ---------------------------
    // 4) DPI — Delta Pressure (approx)
    // ---------------------------
    const ceDelta = CEatm.lastPrice / (CEatm.lastPrice + PEatm.lastPrice + 1);
    const peDelta = 1 - ceDelta;
    const dpi =
        (ceDelta * CEatm.openInterest - peDelta * PEatm.openInterest) /
        (CEatm.openInterest + PEatm.openInterest + 1);

    // ---------------------------
    // 5) STM — Spot Trend Momentum (simple)
    // ---------------------------
    const stm = 0;

    // ---------------------------
    // 6) OCI — Option Chain Imbalance
    // ---------------------------
    let callForce = 0;
    let putForce = 0;

    rows.forEach(r => {
        const dist = Math.abs(r.strikePrice - spot);
        const weight = 1 / (dist + 1);

        callForce += (r.CE.openInterest * weight * (r.CE.lastPrice || 1));
        putForce += (r.PE.openInterest * weight * (r.PE.lastPrice || 1));
    });

    const oci = (putForce - callForce) / (putForce + callForce + 1);

    // ---------------------------
    // FINAL SCORE (weighted)
    // ---------------------------
    const finalScore =
        dop * 0.20 +
        smfi * 0.20 +
        ivSkew * 0.15 +
        dpi * 0.20 +
        stm * 0.10 +
        oci * 0.15;

    return { finalScore, dop, smfi, ivSkew, dpi, stm, oci };
}

function renderSentimentUI(result) {
    if (!result) return;

    const score = result.finalScore;
    let text = "Neutral";

    if (score > 0.5) text = "Strong Bullish";
    else if (score > 0.2) text = "Bullish";
    else if (score < -0.5) text = "Strong Bearish";
    else if (score < -0.2) text = "Bearish";

    document.querySelector(".sentiment-title").textContent = text;
    document.querySelector(".sentiment-score").textContent = score.toFixed(2);

    const s = result;

    document.getElementById("signalBreakdown").innerHTML = `
      ${signalItem("DOP", s.dop)}
      ${signalItem("SMFI", s.smfi)}
      ${signalItem("IV Skew", s.ivSkew)}
      ${signalItem("DPI", s.dpi)}
      ${signalItem("STM", s.stm)}
      ${signalItem("OCI", s.oci)}
    `;
}

function signalItem(label, value) {
    return `
      <div class="signal-item">
        <div class="label">${label}</div>
        <div class="value">${value.toFixed(3)}</div>
      </div>
    `;
}
