// API module for trading signals and analysis endpoints

let historicalChartInstance = null;

async function fetchTradingSignal() {
    const symbol = document.getElementById("symbol").value;
    const expiry = document.getElementById("expiry").value;
    
    const url = new URL("/trading_signal", window.location.origin);
    url.search = new URLSearchParams({ symbol, expiry });
    
    try {
        // Update UI to show loading state
        updateSignalUI('ANALYZING', 'Analyzing market data...', '--', '--');
        
        const response = await safeFetch(url);
        
        if (response.error || !response.success) {
            updateSignalUI('ERROR', 'Failed to fetch signal', '--', '--');
            return;
        }
        
        // Update hero signal card
        const signalText = response.signal === 'CALL' ? '🟢 CALL' : 
                           response.signal === 'PUT' ? '🔴 PUT' : '⚪ NO TRADE';
        
        document.getElementById('heroSignalValue').textContent = signalText;
        document.getElementById('heroConfidence').textContent = `Confidence: ${response.confidence}`;
        
        // Update badge color
        const badge = document.getElementById('heroSignalBadge');
        badge.textContent = response.signal;
        badge.className = 'signal-badge ' + response.signal.toLowerCase();
        
        // Update main signal tab
        updateMainSignalDisplay(response);
        
        // Update key levels
        updateKeyLevels(response.key_levels);
        
        // Update market sentiment badges
        updateSentimentBadges(response.market_sentiment);
        
        // Update signal summary
        document.getElementById('signalSummary').innerHTML = `
            <h4>Analysis Summary</h4>
            <p>${response.analysis_summary?.pcr ? `PCR is <b>${response.analysis_summary.pcr}</b>, Trend is <b>${response.analysis_summary.trend}</b>, RSI is <b>${response.analysis_summary.rsi}</b>` : response.analysis_summary || 'Analysis complete.'}</p>
        `;
        
        console.log('Trading signal loaded successfully');
        
    } catch (error) {
        console.error('Error fetching trading signal:', error);
        updateSignalUI('ERROR', 'Connection error', '--', '--');
    }
}

function updateSignalUI(signal, text, confidence, score) {
    document.getElementById('mainSignalText').textContent = signal;
    document.getElementById('signalConfidence').textContent = confidence;
    document.getElementById('signalSentimentScore').textContent = score;
}

function updateMainSignalDisplay(data) {
    const indicator = document.getElementById('mainSignalIndicator');
    const signalText = document.getElementById('mainSignalText');
    
    // Remove old classes
    indicator.classList.remove('call', 'put');
    
    // Set signal text
    signalText.textContent = data.signal;
    
    // Add appropriate class for animation
    if (data.signal === 'CALL') {
        indicator.classList.add('call');
    } else if (data.signal === 'PUT') {
        indicator.classList.add('put');
    }
    
    // Update details
    document.getElementById('signalConfidence').textContent = data.confidence;
    document.getElementById('signalSentimentScore').textContent = data.sentiment_score?.toFixed(2) || '--';
    document.getElementById('signalUnderlying').textContent = data.underlying_value || '--';
    
    // Update recommendations
    const recContainer = document.getElementById('signalRecommendations');
    if (data.recommended_strikes && data.recommended_strikes.length > 0) {
        recContainer.innerHTML = `
            <div class="levels-grid">
                ${data.recommended_strikes.map(item => `
                    <div class="detail-item" style="min-width: 150px;">
                        <span class="detail-label">${item.type || 'STRIKE'}</span>
                        <span class="detail-value">${item.strike || item}</span>
                        <span class="detail-label" style="font-size: 11px; margin-top: 4px;">${item.reason || ''}</span>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        recContainer.innerHTML = '<p>No specific strike recommendations</p>';
    }
}

function updateKeyLevels(levels) {
    const container = document.getElementById('keyLevelsGrid');
    
    if (!levels || Object.keys(levels).length === 0) {
        container.innerHTML = '<p>No key levels available</p>';
        return;
    }
    
    // Support & resistance list mapping
    container.innerHTML = `
        <div class="detail-item">
            <span class="detail-label">Max Pain</span>
            <span class="detail-value" style="color: var(--primary);">${levels.max_pain || '--'}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Strong Resistance</span>
            <span class="detail-value text-bearish">${levels.resistance || '--'}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Strong Support</span>
            <span class="detail-value text-bullish">${levels.support || '--'}</span>
        </div>
    `;
}

function updateSentimentBadges(sentiment) {
    const container = document.getElementById('sentimentBadges');
    
    if (!sentiment) {
        container.innerHTML = '<p>No sentiment data available</p>';
        return;
    }
    
    const biasClass = sentiment.bias === 'BULLISH' ? 'bg-bullish' :
                     sentiment.bias === 'BEARISH' ? 'bg-bearish' : 'bg-neutral';
    
    container.innerHTML = `
        <div class="card-badge ${biasClass}" style="color: white; padding: 8px 16px;">
            Market Bias: ${sentiment.bias}
        </div>
        <div class="card-badge" style="padding: 8px 16px;">
            Score: ${sentiment.score?.toFixed(2) || '--'}
        </div>
        ${sentiment.key_factors ? sentiment.key_factors.slice(0, 3).map(factor => `
            <div class="card-badge" style="padding: 8px 16px;">
                ${factor}
            </div>
        `).join('') : ''}
    `;
}

async function fetchMarketSentiment() {
    const url = "/market_sentiment";
    
    try {
        const response = await safeFetch(url);
        
        if (response.error || !response.success) {
            return null;
        }
        
        // Update combined sentiment details
        document.getElementById('sentimentScoreValue').textContent = response.combined_score?.toFixed(2) || '--';
        document.getElementById('sentimentBiasDisplay').textContent = response.market_bias || '--';
        document.getElementById('sentimentConfidence').textContent = `Confidence: ${response.confidence || '--'}`;
        
        if (window.drawGauge) {
            // Map news sentiment score (-10 to 10) to (-1 to 1) for the gauge component
            window.drawGauge(response.combined_score / 10);
        }

        // Update global sentiment content
        document.getElementById('globalSentimentContent').innerHTML = `
            <div class="metric-row">
                <span class="metric-label">Score:</span>
                <span class="metric-value">${response.global_sentiment.score?.toFixed(2) || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Classification:</span>
                <span class="metric-value">${response.global_sentiment.overall_classification || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">News Count:</span>
                <span class="metric-value">${response.global_sentiment.news_count || '--'}</span>
            </div>
        `;
        
        // Update Indian sentiment content
        document.getElementById('indianSentimentContent').innerHTML = `
            <div class="metric-row">
                <span class="metric-label">Score:</span>
                <span class="metric-value">${response.indian_sentiment.score?.toFixed(2) || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Classification:</span>
                <span class="metric-value">${response.indian_sentiment.overall_classification || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">News Count:</span>
                <span class="metric-value">${response.indian_sentiment.news_count || '--'}</span>
            </div>
        `;
        
        // Update key factors
        const factorsContainer = document.getElementById('keyFactorsList');
        if (response.key_factors && response.key_factors.length > 0) {
            factorsContainer.innerHTML = response.key_factors.map(factor => `
                <div class="factor-item">${factor}</div>
            `).join('');
        } else {
            factorsContainer.innerHTML = '<p>No key factors identified</p>';
        }
        
        return response;
        
    } catch (error) {
        console.error('Error fetching market sentiment:', error);
        return null;
    }
}

async function fetchPCRAnalysis() {
    const symbol = document.getElementById("symbol").value;
    const expiry = document.getElementById("expiry").value;
    
    const url = new URL("/pcr_analysis", window.location.origin);
    url.search = new URLSearchParams({ symbol, expiry });
    
    try {
        const response = await safeFetch(url);
        
        if (response.error || !response.success) {
            document.getElementById('pcrAnalysisContent').innerHTML = 
                '<p>Failed to load PCR analysis</p>';
            return;
        }
        
        document.getElementById('pcrAnalysisContent').innerHTML = `
            <div class="metric-row">
                <span class="metric-label">Overall OI PCR:</span>
                <span class="metric-value">${response.overall_oi_pcr?.toFixed(2) || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Overall Volume PCR:</span>
                <span class="metric-value">${response.overall_volume_pcr?.toFixed(2) || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Interpretation:</span>
                <span class="metric-value ${response.interpretation?.includes('Bullish') ? 'text-bullish' : 
                                            response.interpretation?.includes('Bearish') ? 'text-bearish' : ''}">
                    ${response.interpretation || '--'}
                </span>
            </div>
        `;
        
    } catch (error) {
        console.error('Error fetching PCR analysis:', error);
        document.getElementById('pcrAnalysisContent').innerHTML = 
            '<p>Error loading PCR analysis</p>';
    }
}

async function fetchMaxPain() {
    const symbol = document.getElementById("symbol").value;
    const expiry = document.getElementById("expiry").value;
    
    const url = new URL("/max_pain", window.location.origin);
    url.search = new URLSearchParams({ symbol, expiry });
    
    try {
        const response = await safeFetch(url);
        
        if (response.error || !response.success) {
            document.getElementById('maxPainContent').innerHTML = 
                '<p>Failed to calculate max pain</p>';
            return;
        }
        
        document.getElementById('maxPainContent').innerHTML = `
            <div class="metric-row">
                <span class="metric-label">Max Pain Strike:</span>
                <span class="metric-value" style="font-size: 24px; color: var(--primary); font-weight: bold;">
                    ${response.max_pain_strike || '--'}
                </span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Total Pain:</span>
                <span class="metric-value">${response.total_pain?.toLocaleString() || '--'}</span>
            </div>
        `;
        
    } catch (error) {
        console.error('Error fetching max pain:', error);
        document.getElementById('maxPainContent').innerHTML = 
            '<p>Error calculating max pain</p>';
    }
}

async function fetchHistoricalAnalysis() {
    const symbol = document.getElementById("symbol").value;
    const fromDate = document.getElementById("fromDate").value;
    const toDate = document.getElementById("toDate").value;
    
    if (!fromDate || !toDate) {
        alert('Please select date range first');
        return;
    }
    
    const url = new URL("/historical_analysis", window.location.origin);
    url.search = new URLSearchParams({ symbol, fromDate, toDate });
    
    try {
        const response = await safeFetch(url);
        
        if (response.error || !response.success) {
            alert('Failed to load historical analysis');
            return;
        }
        
        // Update moving averages
        document.getElementById('movingAveragesContent').innerHTML = `
            <div class="metric-row">
                <span class="metric-label">SMA (20):</span>
                <span class="metric-value">${response.moving_averages?.sma_20 || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">SMA (50):</span>
                <span class="metric-value">${response.moving_averages?.sma_50 || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">SMA (200):</span>
                <span class="metric-value">${response.moving_averages?.sma_200 || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">EMA (9):</span>
                <span class="metric-value">${response.moving_averages?.ema_9 || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">EMA (21):</span>
                <span class="metric-value">${response.moving_averages?.ema_21 || '--'}</span>
            </div>
        `;
        
        // Update trend
        const isBullish = response.trend?.includes('UP');
        const isBearish = response.trend?.includes('DOWN');
        const colorClass = isBullish ? 'text-bullish' : (isBearish ? 'text-bearish' : '');
        document.getElementById('trendContent').innerHTML = `
            <div class="metric-row">
                <span class="metric-label">Trend:</span>
                <span class="metric-value ${colorClass}">
                    ${response.trend || '--'}
                </span>
            </div>
        `;
        
        // Update patterns
        const patternsContainer = document.getElementById('patternsContent');
        if (response.patterns && response.patterns.length > 0) {
            patternsContainer.innerHTML = response.patterns.map(p => `
                <div class="factor-item" style="margin-bottom: 8px;">
                    <b>${p.pattern}</b> on ${p.date} (${p.significance})
                </div>
            `).join('');
        } else {
            patternsContainer.innerHTML = '<p>No patterns detected</p>';
        }
        
        // Update RSI
        document.getElementById('rsiContent').innerHTML = `
            <div class="metric-row">
                <span class="metric-label">RSI Value:</span>
                <span class="metric-value">${response.rsi?.toFixed(2) || '--'}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Status:</span>
                <span class="metric-value ${response.rsi > 70 ? 'text-bearish' : 
                                            response.rsi < 30 ? 'text-bullish' : ''}">
                    ${response.rsi > 70 ? 'Overbought' : response.rsi < 30 ? 'Oversold' : 'Neutral'}
                </span>
            </div>
        `;

        // Render historical close chart
        if (response.historical_data && response.historical_data.length > 0) {
            drawHistoricalChart(response.historical_data);
        }
        
    } catch (error) {
        console.error('Error fetching historical analysis:', error);
        alert('Error loading historical analysis');
    }
}

function drawHistoricalChart(spotData) {
    const ctx = document.getElementById("historicalChart");
    if (!ctx) return;

    if (historicalChartInstance) {
        historicalChartInstance.destroy();
    }

    const theme = window.getChartTheme ? window.getChartTheme() : { grid: "rgba(0,0,0,0.1)", text: "#333", tooltipBg: "#f4f4f4" };

    historicalChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: spotData.map(x => x.date),
            datasets: [
                {
                    label: "Spot Close",
                    data: spotData.map(x => x.close),
                    borderColor: "#3d7cff",
                    backgroundColor: "rgba(61, 124, 255, 0.15)",
                    borderWidth: 2,
                    tension: 0.15,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: theme.text } },
                tooltip: {
                    backgroundColor: theme.tooltipBg,
                    titleColor: theme.text,
                    bodyColor: theme.text
                }
            },
            scales: {
                x: { 
                    ticks: { color: theme.text }, 
                    grid: { color: theme.grid }
                },
                y: { 
                    ticks: { color: theme.text }, 
                    grid: { color: theme.grid }
                }
            }
        }
    });
}

// Expose functions to window
window.fetchTradingSignal = fetchTradingSignal;
window.fetchMarketSentiment = fetchMarketSentiment;
window.fetchPCRAnalysis = fetchPCRAnalysis;
window.fetchMaxPain = fetchMaxPain;
window.fetchHistoricalAnalysis = fetchHistoricalAnalysis;
window.drawHistoricalChart = drawHistoricalChart;
