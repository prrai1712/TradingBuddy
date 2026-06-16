document.addEventListener("DOMContentLoaded", () => {
  const btns = document.querySelectorAll(".nav-btn");
  const sections = document.querySelectorAll(".tab-section");

  btns.forEach(btn => {
    btn.addEventListener("click", async () => {
      const tab = btn.dataset.tab;
      if (!tab) return;

      // highlight tab
      btns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      // show section
      sections.forEach(sec => {
        sec.classList.toggle("active", sec.id === tab);
      });

      // 🔥 Load Option Chain
      if (tab === "chain") {
        const box = document.getElementById("chainContainer");
        box.innerHTML = "<p style='opacity:0.4'>Loading chain...</p>";

        const chain = await loadFullChain();
        renderChainTable(chain);
      }

      // 🔥 Load Signals
      if (tab === "signals" && window.fetchTradingSignal) {
        window.fetchTradingSignal();
      }

      // 🔥 Load Sentiment
      if (tab === "sentiment") {
        if (window.fetchMarketSentiment) window.fetchMarketSentiment();
        if (window.fetchPCRAnalysis) window.fetchPCRAnalysis();
        if (window.fetchMaxPain) window.fetchMaxPain();
      }

      // 🔥 Load Technical Analysis
      if (tab === "technical" && window.fetchHistoricalAnalysis) {
        window.fetchHistoricalAnalysis();
      }
    });
  });
});
