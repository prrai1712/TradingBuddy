// UI module for trading signals display

function updateHeroSignal(signal, confidence) {
    const signalValue = document.getElementById('heroSignalValue');
    const heroConfidence = document.getElementById('heroConfidence');
    const heroBadge = document.getElementById('heroSignalBadge');
    
    if (!signalValue || !heroConfidence) return;
    
    let signalText = '⚪ NO TRADE';
    let badgeClass = 'neutral';
    
    if (signal === 'CALL') {
        signalText = '🟢 CALL';
        badgeClass = 'call';
    } else if (signal === 'PUT') {
        signalText = '🔴 PUT';
        badgeClass = 'put';
    }
    
    signalValue.textContent = signalText;
    heroConfidence.textContent = `Confidence: ${confidence || '--'}`;
    
    if (heroBadge) {
        heroBadge.textContent = signal || 'ANALYZING';
        heroBadge.className = `signal-badge ${badgeClass}`;
    }
}

function updateLiveDataUI(data) {
    // Update NIFTY Live in header
    const headerNifty = document.getElementById('headerNiftyLive');
    if (headerNifty && data.nifty_spot) {
        headerNifty.textContent = `NIFTY: ${data.nifty_spot}`;
    }
    
    // Update CE title and data
    const ceTitle = document.getElementById('ceTitle');
    const ceBox = document.getElementById('ceBox');
    
    if (ceTitle && data.CE) {
        ceTitle.textContent = `${data.strike || '--'} CE`;
        
        if (data.CE.error) {
            ceBox.innerHTML = `<div class="loading-state">Error: ${data.CE.error}</div>`;
        } else {
            const totalMoneyValue = (Number(data.CE.traded_value) / 1_000_000).toFixed(2);
            ceBox.innerHTML = `
                <p><span>LTP:</span> <b>${data.CE.ltp}</b></p>
                <p><span>Open:</span> <span>${data.CE.open}</span></p>
                <p><span>High:</span> <span>${data.CE.high}</span></p>
                <p><span>Low:</span> <span>${data.CE.low}</span></p>
                <p><span>OI:</span> <span>${data.CE.oi}</span></p>
                <p><span>OI Change:</span> <span>${data.CE.oi_change}</span></p>
                <p><span>Turnover:</span> <span>${totalMoneyValue}M</span></p>
                <p><small style="color: var(--text-light);">Updated: ${data.CE.last_update}</small></p>
            `;
        }
    }
    
    // Update PE title and data
    const peTitle = document.getElementById('peTitle');
    const peBox = document.getElementById('peBox');
    
    if (peTitle && data.PE) {
        peTitle.textContent = `${data.strike || '--'} PE`;
        
        if (data.PE.error) {
            peBox.innerHTML = `<div class="loading-state">Error: ${data.PE.error}</div>`;
        } else {
            const totalMoneyValue = (Number(data.PE.traded_value) / 1_000_000).toFixed(2);
            peBox.innerHTML = `
                <p><span>LTP:</span> <b>${data.PE.ltp}</b></p>
                <p><span>Open:</span> <span>${data.PE.open}</span></p>
                <p><span>High:</span> <span>${data.PE.high}</span></p>
                <p><span>Low:</span> <span>${data.PE.low}</span></p>
                <p><span>OI:</span> <span>${data.PE.oi}</span></p>
                <p><span>OI Change:</span> <span>${data.PE.oi_change}</span></p>
                <p><span>Turnover:</span> <span>${totalMoneyValue}M</span></p>
                <p><small style="color: var(--text-light);">Updated: ${data.PE.last_update}</small></p>
            `;
        }
    }
    
    // Update ratios
    const ratioBox = document.getElementById('ratioBox');
    if (ratioBox && data.CE && data.PE && !data.CE.error && !data.PE.error) {
        const oiRatio = (data.PE.oi / data.CE.oi).toFixed(2);
        const valueRatio = (data.PE.traded_value / data.CE.traded_value).toFixed(2);
        const premiumRatio = (data.PE.ltp / data.CE.ltp).toFixed(2);
        
        ratioBox.innerHTML = `
            <p><span>OI Ratio (PE/CE):</span> <b>${oiRatio}</b></p>
            <p><span>Value Ratio (PE/CE):</span> <b>${valueRatio}</b></p>
            <p><span>Premium Ratio (PE/CE):</span> <b>${premiumRatio}</b></p>
        `;
    }
}

function updatePCRBox(pcrData) {
    const pcrBox = document.getElementById('pcrBox');
    if (!pcrBox) return;
    
    if (!pcrData || pcrData.error) {
        pcrBox.innerHTML = '<div class="loading-state">No PCR data</div>';
        return;
    }
    
    const interpretation = getPCRInterpretation(pcrData.overall_oi_pcr);
    
    pcrBox.innerHTML = `
        <p><span>OI PCR:</span> <b>${pcrData.overall_oi_pcr?.toFixed(2) || '--'}</b></p>
        <p><span>Volume PCR:</span> <span>${pcrData.overall_volume_pcr?.toFixed(2) || '--'}</span></p>
        <p><span>Signal:</span> <span class="${interpretation.class}">${interpretation.text}</span></p>
    `;
}

function getPCRInterpretation(pcr) {
    if (!pcr) return { text: '--', class: '' };
    
    if (pcr > 1.5) return { text: 'Very Bullish', class: 'text-bullish' };
    if (pcr > 1.2) return { text: 'Bullish', class: 'text-bullish' };
    if (pcr > 0.8) return { text: 'Neutral', class: '' };
    if (pcr > 0.5) return { text: 'Bearish', class: 'text-bearish' };
    return { text: 'Very Bearish', class: 'text-bearish' };
}

function filterChain(filterType) {
    // Update active button
    document.querySelectorAll('.btn-filter').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Re-render chain table with filter
    const currentChain = window.currentOptionChain;
    if (currentChain) {
        renderChainTable(currentChain, filterType);
    }
}

// Make filterChain available globally
window.filterChain = filterChain;
