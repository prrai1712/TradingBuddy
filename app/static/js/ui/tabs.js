document.addEventListener("DOMContentLoaded", () => {
  const btns = document.querySelectorAll(".tab-btn");
  const sections = document.querySelectorAll(".tab-section");

  btns.forEach(btn => {
    btn.addEventListener("click", async () => {
      const tab = btn.dataset.tab;

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
        box.innerHTML = "<p style='opacity:0.4'>Loading chain</p>";

        const chain = await loadFullChain();
        renderChainTable(chain);
      }

      // 🔥 Load Sentiment
      if (tab === "sentiment") {
        const chain = await loadFullChain();
        const sentiment = await computeSentiment(chain);

        renderSentimentUI(sentiment);
        drawGauge(sentiment.finalScore);
      }
    });
  });
});
