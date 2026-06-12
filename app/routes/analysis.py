# app/routes/analysis.py
"""
Trading Signal and Analysis Routes
Provides endpoints for option chain analysis, sentiment analysis, and trading signals
"""

from flask import Blueprint, request, jsonify
import requests
from datetime import datetime
from app.utils.nse_headers import get_nse_headers
from app.utils.option_analyzer import (
    OptionChainAnalyzer, 
    HistoricalPatternAnalyzer, 
    SentimentAnalyzer,
    generate_trading_signal
)
from app.utils.news_sentiment import NewsSentimentAnalyzer, get_market_sentiment_report

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.get("/trading_signal")
def trading_signal():
    """
    Generate CALL/PUT trading signal based on comprehensive analysis
    
    Query Parameters:
    - symbol: Stock/Index symbol (default: NIFTY)
    - expiry: Expiry date in YYYY-MM-DD format
    
    Returns:
    - signal: CALL, PUT, or NO_TRADE
    - confidence: HIGH, MEDIUM, or LOW
    - recommended_strikes: List of recommended strike prices
    - full analysis data
    """
    symbol = request.args.get("symbol", "NIFTY").upper()
    expiry = request.args.get("expiry")
    
    try:
        # Fetch option chain data
        chain_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        if expiry:
            chain_url += f"&expiryDate={expiry}"
        
        headers = get_nse_headers()
        headers["referer"] = "https://www.nseindia.com/option-chain"
        headers["accept"] = "application/json"
        
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        
        chain_resp = session.get(chain_url, headers=headers, timeout=10)
        option_chain_data = chain_resp.json()
        
        # Fetch historical data for the underlying
        hist_data = _fetch_historical_data(symbol, session, headers)
        
        # Get market sentiment
        sentiment_analyzer = NewsSentimentAnalyzer()
        market_sentiment = sentiment_analyzer.get_combined_market_sentiment()
        
        # Generate trading signal
        signal_result = generate_trading_signal(
            option_chain=option_chain_data,
            historical_data=hist_data,
            global_sentiment={
                'composite_score': market_sentiment['combined_score']
            }
        )
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'signal': signal_result['signal'],
            'confidence': signal_result['confidence'],
            'sentiment_score': signal_result['sentiment_score'],
            'underlying_value': signal_result['underlying_value'],
            'recommended_strikes': signal_result['recommended_strikes'],
            'key_levels': signal_result['key_levels'],
            'analysis_summary': signal_result['analysis_summary'],
            'market_sentiment': {
                'bias': market_sentiment['market_bias'],
                'score': market_sentiment['combined_score'],
                'key_factors': market_sentiment['key_factors']
            },
            'risk_warning': 'Trading derivatives involves substantial risk. This is not investment advice.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to generate trading signal'
        }), 500


@analysis_bp.get("/option_chain_analysis")
def option_chain_analysis():
    """
    Deep analysis of option chain data
    
    Query Parameters:
    - symbol: Stock/Index symbol (default: NIFTY)
    - expiry: Expiry date in YYYY-MM-DD format
    
    Returns:
    - PCR analysis
    - Max Pain calculation
    - Support/Resistance levels
    - OI Buildup patterns
    - Greeks approximation
    """
    symbol = request.args.get("symbol", "NIFTY").upper()
    expiry = request.args.get("expiry")
    
    try:
        # Fetch option chain
        chain_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        if expiry:
            chain_url += f"&expiryDate={expiry}"
        
        headers = get_nse_headers()
        headers["referer"] = "https://www.nseindia.com/option-chain"
        
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        
        resp = session.get(chain_url, headers=headers, timeout=10)
        option_chain_data = resp.json()
        
        # Analyze
        analyzer = OptionChainAnalyzer(option_chain_data)
        analysis = analyzer.get_comprehensive_analysis()
        
        return jsonify({
            'success': True,
            'timestamp': analysis['timestamp'],
            'symbol': symbol,
            'underlying_value': analysis['underlying_value'],
            'pcr_analysis': analysis['pcr_analysis'],
            'max_pain': analysis['max_pain'],
            'support_resistance': analysis['support_resistance'],
            'oi_buildup': analysis['oi_buildup'],
            'greeks_approximation': analysis['greeks_approx']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analysis_bp.get("/historical_analysis")
def historical_analysis():
    """
    Analyze historical price patterns and trends
    
    Query Parameters:
    - symbol: Stock/Index symbol (default: NIFTY)
    - fromDate: Start date in DD-MM-YYYY format
    - toDate: End date in DD-MM-YYYY format
    
    Returns:
    - Moving averages (SMA, EMA)
    - Trend direction
    - Candlestick patterns detected
    - RSI value
    """
    symbol = request.args.get("symbol", "NIFTY").upper()
    from_date = request.args.get("fromDate")
    to_date = request.args.get("toDate")
    
    if not from_date or not to_date:
        return jsonify({
            'success': False,
            'error': 'Missing date parameters'
        }), 400
    
    try:
        # Fetch historical data
        hist_data = _fetch_historical_data_raw(symbol, from_date, to_date)
        
        # Analyze
        analyzer = HistoricalPatternAnalyzer(hist_data)
        analysis = analyzer.get_historical_analysis()
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'from_date': from_date,
            'to_date': to_date,
            'data_points': analysis['data_points'],
            'moving_averages': analysis['moving_averages'],
            'trend': analysis['trend'],
            'patterns': analysis['patterns'],
            'rsi': analysis['rsi']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analysis_bp.get("/market_sentiment")
def market_sentiment():
    """
    Get market sentiment analysis from news
    
    Returns:
    - Global sentiment score
    - Indian sentiment score
    - Combined market bias
    - Key factors affecting sentiment
    """
    try:
        sentiment_report = get_market_sentiment_report()
        
        return jsonify({
            'success': True,
            'timestamp': sentiment_report['timestamp'],
            'combined_score': sentiment_report['combined_score'],
            'market_bias': sentiment_report['market_bias'],
            'confidence': sentiment_report['confidence'],
            'global_sentiment': {
                'score': sentiment_report['global_sentiment']['composite_score'],
                'classification': sentiment_report['global_sentiment']['overall_classification'],
                'news_count': sentiment_report['global_sentiment']['news_count']
            },
            'indian_sentiment': {
                'score': sentiment_report['indian_sentiment']['composite_score'],
                'classification': sentiment_report['indian_sentiment']['overall_classification'],
                'news_count': sentiment_report['indian_sentiment']['news_count']
            },
            'key_factors': sentiment_report['key_factors']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analysis_bp.get("/max_pain")
def max_pain():
    """
    Calculate Max Pain point for given symbol and expiry
    
    Query Parameters:
    - symbol: Stock/Index symbol (default: NIFTY)
    - expiry: Expiry date in YYYY-MM-DD format
    
    Returns:
    - max_pain_strike: Strike price with minimum pain
    - pain_values: Pain calculations for top strikes
    """
    symbol = request.args.get("symbol", "NIFTY").upper()
    expiry = request.args.get("expiry")
    
    try:
        # Fetch option chain
        chain_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        if expiry:
            chain_url += f"&expiryDate={expiry}"
        
        headers = get_nse_headers()
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        
        resp = session.get(chain_url, headers=headers, timeout=10)
        option_chain_data = resp.json()
        
        # Calculate max pain
        analyzer = OptionChainAnalyzer(option_chain_data)
        max_pain_result = analyzer.find_max_pain()
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'max_pain_strike': max_pain_result['max_pain_strike'],
            'total_pain': max_pain_result['total_pain'],
            'top_pain_points': max_pain_result['all_pain_points']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analysis_bp.get("/pcr_analysis")
def pcr_analysis():
    """
    Get Put-Call Ratio analysis
    
    Query Parameters:
    - symbol: Stock/Index symbol (default: NIFTY)
    - expiry: Expiry date in YYYY-MM-DD format
    
    Returns:
    - Overall OI PCR
    - Overall Volume PCR
    - Strike-wise PCR
    """
    symbol = request.args.get("symbol", "NIFTY").upper()
    expiry = request.args.get("expiry")
    
    try:
        # Fetch option chain
        chain_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        if expiry:
            chain_url += f"&expiryDate={expiry}"
        
        headers = get_nse_headers()
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        
        resp = session.get(chain_url, headers=headers, timeout=10)
        option_chain_data = resp.json()
        
        # Calculate PCR
        analyzer = OptionChainAnalyzer(option_chain_data)
        pcr_result = analyzer.calculate_pcr()
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'overall_oi_pcr': pcr_result['overall_oi_pcr'],
            'overall_volume_pcr': pcr_result['overall_volume_pcr'],
            'strike_wise_pcr': pcr_result['strike_wise_pcr'][:10],  # Top 10 strikes
            'interpretation': _interpret_pcr(pcr_result['overall_oi_pcr'])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _fetch_historical_data(symbol: str, session: requests.Session, headers: dict) -> list:
    """Fetch historical data for analysis"""
    # Get last 200 days of data
    end_date = datetime.now()
    start_date = end_date.replace(day=end_date.day - 200)
    
    from_date = start_date.strftime("%d-%m-%Y")
    to_date = end_date.strftime("%d-%m-%Y")
    
    return _fetch_historical_data_raw(symbol, from_date, to_date)


def _fetch_historical_data_raw(symbol: str, from_date: str, to_date: str) -> list:
    """Fetch raw historical data"""
    names = {
        "NIFTY": "NIFTY 50",
        "BANKNIFTY": "NIFTY BANK",
        "FINNIFTY": "NIFTY FIN SERVICE"
    }
    index_name = names.get(symbol.upper(), "NIFTY 50")
    
    url = (
        "https://www.nseindia.com/api/historical/indicesHistory"
        f"?indexType={index_name.replace(' ', '%20')}"
        f"&from={from_date}&to={to_date}"
    )
    
    headers = {
        "user-agent": "Mozilla/5.0",
        "referer": "https://www.nseindia.com/",
    }
    
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    
    rows = data.get("data", {}).get("indexCloseOnlineRecords", [])
    
    output = []
    for it in rows:
        ts = it.get("EOD_TIMESTAMP")
        close = it.get("EOD_CLOSE_INDEX_VAL")
        open_val = it.get("EOD_OPEN_INDEX_VAL")
        high = it.get("EOD_HIGH_INDEX_VAL")
        low = it.get("EOD_LOW_INDEX_VAL")
        
        if not ts or close is None:
            continue
        
        output.append({
            'date': ts,
            'open': open_val,
            'high': high,
            'low': low,
            'close': close
        })
    
    return output


def _interpret_pcr(pcr_value: float) -> str:
    """Interpret PCR value"""
    if pcr_value > 1.5:
        return "Very Bullish - Strong put writing indicates bullish sentiment"
    elif pcr_value > 1.2:
        return "Bullish - More puts than calls suggests upside bias"
    elif pcr_value > 0.8:
        return "Neutral - Balanced market sentiment"
    elif pcr_value > 0.5:
        return "Bearish - More calls than puts suggests downside bias"
    else:
        return "Very Bearish - Heavy call writing indicates bearish sentiment"
