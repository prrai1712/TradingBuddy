# Advanced Option Chain Analysis & Trading Signal System

## Overview

This system provides comprehensive option chain analysis with deep calculations, historical pattern recognition, global/Indian market sentiment analysis, and generates CALL/PUT trading signals.

## New Features

### 1. **Advanced Option Chain Analysis** (`/app/utils/option_analyzer.py`)

#### Key Algorithms:

- **PCR (Put-Call Ratio) Analysis**
  - Overall OI PCR and Volume PCR
  - Strike-wise PCR calculation
  - Market sentiment interpretation

- **Max Pain Calculation**
  - Identifies strike price where option writers have minimum loss
  - Calculates pain values for all strikes
  - Returns top 5 pain points

- **Greeks Approximation**
  - ATM (At-The-Money) strike identification
  - Implied Volatility estimation
  - Price and OI change analysis

- **Support & Resistance Identification**
  - Based on highest OI concentrations
  - Top 3 support and resistance levels
  - Strongest levels identification

- **OI Buildup Pattern Analysis**
  - Long Buildup (Price ↑, OI ↑)
  - Short Buildup (Price ↓, OI ↑)
  - Long Unwinding (Price ↓, OI ↓)
  - Short Covering (Price ↑, OI ↓)

### 2. **Historical Pattern Analysis** (`/app/utils/option_analyzer.py`)

- **Moving Averages**
  - SMA: 20, 50, 200 periods
  - EMA: 9, 21 periods

- **Trend Detection**
  - STRONG_UPTREND
  - UPTREND
  - SIDEWAYS
  - DOWNTREND
  - STRONG_DOWNTREND

- **Candlestick Patterns**
  - Doji detection
  - Bullish Engulfing
  - Bearish Engulfing

- **RSI Calculation**
  - 14-period RSI
  - Overbought/Oversold identification

### 3. **News Sentiment Analysis** (`/app/utils/news_sentiment.py`)

- **Global Market Sentiment**
  - Analyzes international market news
  - Sentiment scoring (-10 to +10)
  - Impact assessment (HIGH/MEDIUM/LOW)

- **Indian Market Sentiment**
  - Domestic news analysis
  - RBI policy impact
  - Corporate earnings sentiment

- **Combined Market Bias**
  - Weighted scoring (40% Global, 60% Indian)
  - BULLISH/BEARISH/NEUTRAL classification
  - Key factors identification

### 4. **Trading Signal Generation**

Combines all analyses to generate:
- **Signal**: CALL, PUT, or NO_TRADE
- **Confidence**: HIGH, MEDIUM, or LOW
- **Recommended Strikes**: ITM and ATM options
- **Key Levels**: Support, Resistance, Max Pain
- **Risk Factors**: All influencing factors

---

## API Endpoints

### 🎯 **Trading Signal Endpoint**

```
GET /trading_signal?symbol=NIFTY&expiry=2025-06-30
```

**Response:**
```json
{
  "success": true,
  "signal": "CALL",
  "confidence": "MEDIUM",
  "sentiment_score": 35.5,
  "underlying_value": 22500,
  "recommended_strikes": [
    {"type": "ITM_CALL", "strike": 22400, "reason": "Support level"},
    {"type": "ATM_CALL", "strike": 22500, "reason": "Balanced risk/reward"}
  ],
  "key_levels": {
    "support": 22400,
    "resistance": 22600,
    "max_pain": 22500
  },
  "analysis_summary": {
    "pcr": 1.15,
    "trend": "UPTREND",
    "rsi": 58.5,
    "patterns_detected": 2
  },
  "market_sentiment": {
    "bias": "BULLISH",
    "score": 4.2,
    "key_factors": ["Positive domestic sentiment"]
  }
}
```

---

### 📊 **Option Chain Analysis**

```
GET /option_chain_analysis?symbol=NIFTY&expiry=2025-06-30
```

**Returns:**
- PCR analysis (overall & strike-wise)
- Max Pain calculation
- Support/Resistance levels
- OI Buildup patterns
- Greeks approximation

---

### 📈 **Historical Analysis**

```
GET /historical_analysis?symbol=NIFTY&fromDate=01-01-2025&toDate=12-06-2025
```

**Returns:**
- Moving averages (SMA, EMA)
- Trend direction
- Candlestick patterns detected
- RSI value

---

### 🌍 **Market Sentiment**

```
GET /market_sentiment
```

**Returns:**
- Global sentiment score
- Indian sentiment score
- Combined market bias
- Key factors affecting sentiment

---

### 😫 **Max Pain**

```
GET /max_pain?symbol=NIFTY&expiry=2025-06-30
```

**Returns:**
- Max pain strike price
- Total pain value
- Top pain points

---

### 📊 **PCR Analysis**

```
GET /pcr_analysis?symbol=NIFTY&expiry=2025-06-30
```

**Returns:**
- Overall OI PCR
- Overall Volume PCR
- Strike-wise PCR (top 10)
- Interpretation

---

## Existing Endpoints (Updated)

All existing endpoints now use the latest NSE API endpoints:

- `/full_chain` - Complete option chain data
- `/live_option_data` - Live option prices
- `/nifty_spot` - Historical spot prices
- `/open_price` - Historical option prices
- `/expiry_dates` - Available expiry dates

---

## Algorithm Details

### Sentiment Score Calculation

The final sentiment score (-100 to +100) is calculated using:

1. **PCR Analysis (30% weight)**
   - PCR > 1.2: +25 (Bullish)
   - PCR > 1.0: +10 (Moderately Bullish)
   - PCR < 0.8: -25 (Bearish)
   - PCR < 1.0: -10 (Moderately Bearish)

2. **RSI Analysis (20% weight)**
   - RSI > 70: -15 (Overbought)
   - RSI < 30: +15 (Oversold)
   - RSI > 60: +5 (Strong)
   - RSI < 40: -5 (Weak)

3. **Trend Analysis (30% weight)**
   - STRONG_UPTREND: +30
   - UPTREND: +20
   - SIDEWAYS: 0
   - DOWNTREND: -20
   - STRONG_DOWNTREND: -30

4. **Global Sentiment (20% weight)**
   - Scaled composite score

### Signal Generation Logic

```python
if score >= 30:
    signal = "CALL"
    confidence = "HIGH" if score >= 50 else "MEDIUM"
elif score <= -30:
    signal = "PUT"
    confidence = "HIGH" if score <= -50 else "MEDIUM"
else:
    signal = "NO_TRADE"
    confidence = "LOW"
```

---

## Usage Examples

### Python Example

```python
import requests

# Get trading signal
response = requests.get(
    'http://localhost:5000/trading_signal',
    params={'symbol': 'NIFTY', 'expiry': '2025-06-30'}
)
data = response.json()

print(f"Signal: {data['signal']}")
print(f"Confidence: {data['confidence']}")
print(f"Recommended Strikes: {data['recommended_strikes']}")
```

### JavaScript Example

```javascript
// Get option chain analysis
fetch('/option_chain_analysis?symbol=NIFTY')
  .then(response => response.json())
  .then(data => {
    console.log('PCR:', data.pcr_analysis.overall_oi_pcr);
    console.log('Max Pain:', data.max_pain.max_pain_strike);
    console.log('Support:', data.support_resistance.strongest_support);
  });

// Get trading signal
fetch('/trading_signal?symbol=NIFTY')
  .then(response => response.json())
  .then(data => {
    if (data.signal === 'CALL') {
      console.log('🟢 BUY CALL');
    } else if (data.signal === 'PUT') {
      console.log('🔴 BUY PUT');
    } else {
      console.log('⚪ NO TRADE');
    }
  });
```

---

## Risk Warning

⚠️ **Trading derivatives involves substantial risk of loss and is not suitable for every investor.**

- This system provides analytical tools only
- Signals are based on historical data and mathematical models
- Past performance does not guarantee future results
- Always do your own research before trading
- Never trade with money you cannot afford to lose

---

## Integration with Frontend

The analysis endpoints return JSON data that can be easily integrated into any frontend framework:

- React/Vue/Angular components
- Real-time dashboards
- Mobile applications
- Trading bots

---

## Production Deployment Notes

### For News Sentiment (Production Ready)

To enable real news analysis, integrate with:

1. **NewsAPI.org** - Global news
2. **Moneycontrol API** - Indian market news
3. **Economic Times API** - Business news
4. **NSE/BSE Announcements** - Corporate filings

Update `news_sentiment.py` methods:
- `fetch_global_news()` - Replace with actual API calls
- `fetch_indian_news()` - Replace with actual API calls

### Rate Limiting

- NSE API has rate limits
- Implement caching for frequently accessed data
- Use session management for efficient requests

### Error Handling

All endpoints include comprehensive error handling:
- Network timeouts
- Invalid data formats
- API unavailability
- Missing parameters

---

## File Structure

```
/workspace
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes/
│   │   ├── analysis.py          # NEW: Analysis & signal endpoints
│   │   ├── full_chain.py        # Updated: Latest NSE API
│   │   ├── live_data.py         # Updated: Latest NSE API
│   │   ├── nifty.py             # Updated: Latest NSE API
│   │   ├── option_price.py      # Updated: Latest NSE API
│   │   └── expiry.py            # Updated: Latest NSE API
│   └── utils/
│       ├── option_analyzer.py   # NEW: Deep analysis algorithms
│       ├── news_sentiment.py    # NEW: News sentiment analysis
│       ├── nse_headers.py       # NSE API headers
│       └── formatters.py        # Data formatting utilities
├── service.py                   # Application entry point
└── requirements.txt             # Python dependencies
```

---

## Testing

Test the new endpoints:

```bash
# Test trading signal
curl "http://localhost:5000/trading_signal?symbol=NIFTY"

# Test option chain analysis
curl "http://localhost:5000/option_chain_analysis?symbol=NIFTY"

# Test market sentiment
curl "http://localhost:5000/market_sentiment"

# Test max pain
curl "http://localhost:5000/max_pain?symbol=NIFTY"

# Test PCR analysis
curl "http://localhost:5000/pcr_analysis?symbol=NIFTY"
```

---

## Performance Optimization

- **Caching**: Implement Redis caching for option chain data
- **Async Processing**: Use Celery for heavy calculations
- **Database**: Store historical data in PostgreSQL/MongoDB
- **WebSocket**: Real-time updates for live signals

---

## Future Enhancements

1. **Machine Learning Models**
   - Pattern recognition with CNN
   - Price prediction with LSTM
   - Sentiment analysis with NLP

2. **Additional Indicators**
   - Bollinger Bands
   - MACD
   - Stochastic Oscillator
   - Volatility Index (VIX)

3. **Portfolio Management**
   - Position tracking
   - P&L calculation
   - Risk management alerts

4. **Backtesting Engine**
   - Historical signal testing
   - Strategy optimization
   - Performance metrics

---

## License

This software is provided for educational purposes only.

---

## Support

For issues and feature requests, please check the documentation or contact support.
