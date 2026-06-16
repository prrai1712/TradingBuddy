# app/routes/analysis.py
"""
Trading Signal and Analysis Routes
Provides endpoints for option chain analysis, sentiment analysis, and trading signals
"""

from flask import Blueprint, request, jsonify
import requests
from datetime import datetime, timedelta
from app.utils.nse_headers import get_nse_headers
from app.utils.option_chain_helper import fetch_unblocked_option_chain
from app.utils.option_analyzer import (
    OptionChainAnalyzer, 
    HistoricalPatternAnalyzer, 
    SentimentAnalyzer,
    generate_trading_signal
)
from app.utils.news_sentiment import NewsSentimentAnalyzer, get_market_sentiment_report

analysis_bp = Blueprint("analysis", __name__)


def _get_default_expiry(symbol: str) -> str:
    # Fetch active expiry dates for current year to get a default
    current_year = str(datetime.now().year)
    url = f"https://www.nseindia.com/api/historicalOR/meta/foCPV/expireDts?instrument=OPTIDX&symbol={symbol}&year={current_year}"
    headers = {
        "user-agent": "Mozilla/5.0",
        "referer": "https://www.nseindia.com/",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        dates = resp.json().get("expiresDts", [])
        if dates:
            exp_raw = dates[0] # e.g. "02-JAN-2025"
            d, mmm, y = exp_raw.split("-")
            months = [
                "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
            ]
            m = str(months.index(mmm.upper()) + 1).zfill(2)
            return f"{y}-{m}-{d}"
    except Exception as e:
        print(f"Error fetching default expiry: {e}")
    # Return a fallback default expiry
    return "2026-06-25"


def _fetch_historical_data_raw(symbol: str, from_date: str, to_date: str, expiry: str = None) -> list:
    """Fetch raw historical data using unblocked foCPV endpoint"""
    if not expiry:
        expiry = _get_default_expiry(symbol)
        
    try:
        y, m, d = expiry.split("-")
        months = [
            "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
            "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
        ]
        expiry_final = f"{d}-{months[int(m)-1]}-{y}"
    except:
        y = "2026"
        expiry_final = "25-JUN-2026"

    # We use a middle/approximate strike price to get the underlying index values.
    strikes = {
        "NIFTY": "24000",
        "BANKNIFTY": "50000",
        "FINNIFTY": "22000"
    }
    strike = strikes.get(symbol.upper(), "24000")

    url = "https://www.nseindia.com/api/historicalOR/foCPV"
    params = {
        "from": from_date,
        "to": to_date,
        "instrumentType": "OPTIDX",
        "symbol": symbol,
        "year": y,
        "expiryDate": expiry_final,
        "optionType": "CE",
        "strikePrice": strike,
    }
    headers = {
        "user-agent": "Mozilla/5.0",
        "referer": "https://www.nseindia.com/",
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        rows = resp.json().get("data", [])
    except Exception as e:
        print(f"Error in _fetch_historical_data_raw: {e}")
        rows = []

    output = []
    for it in rows:
        ts = it.get("FH_TIMESTAMP")
        close = it.get("FH_UNDERLYING_VALUE")
        open_val = it.get("FH_OPENING_PRICE")
        high = it.get("FH_TRADE_HIGH_PRICE")
        low = it.get("FH_TRADE_LOW_PRICE")

        if not ts or close is None:
            continue

        output.append({
            'date': ts,
            'open': open_val,
            'high': high,
            'low': low,
            'close': close
        })

    # The historical analyzer expects chronological data (oldest first).
    # Since foCPV returns reverse chronological, let's reverse the output.
    output.reverse()
    return output


def _fetch_historical_data(symbol: str, session: requests.Session, headers: dict, expiry: str = None) -> list:
    """Fetch historical data for analysis (last 200 days)"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=200)
    
    from_date = start_date.strftime("%d-%m-%Y")
    to_date = end_date.strftime("%d-%m-%Y")
    
    return _fetch_historical_data_raw(symbol, from_date, to_date, expiry)


@analysis_bp.get("/trading_signal")
def trading_signal():
    """
    Generate CALL/PUT trading signal based on comprehensive analysis
    """
    symbol = request.args.get("symbol", "NIFTY").upper()
    expiry = request.args.get("expiry")
    
    try:
        # Fetch option chain data
        option_chain_data = fetch_unblocked_option_chain(symbol, expiry)
        
        # Resolve expiry if not passed
        if not expiry and option_chain_data.get("records", {}).get("expiryDates"):
            exp_raw = option_chain_data["records"]["expiryDates"][0]
            try:
                # convert e.g. 02-JAN-2025 to YYYY-MM-DD
                d, mmm, y = exp_raw.split("-")
                months = [
                    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
                ]
                m = str(months.index(mmm.upper()) + 1).zfill(2)
                expiry = f"{y}-{m}-{d}"
            except:
                pass
        
        # Fetch historical data for the underlying
        session = requests.Session()
        headers = get_nse_headers()
        hist_data = _fetch_historical_data(symbol, session, headers, expiry)
        
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
        import sys
        import traceback
        print(f"Error generating trading signal: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to generate trading signal'
        }), 500


@analysis_bp.get("/option_chain_analysis")
def option_chain_analysis():
    """
    Deep analysis of option chain data
    """
    symbol = request.args.get("symbol", "NIFTY").upper()
    expiry = request.args.get("expiry")
    
    try:
        # Fetch option chain
        option_chain_data = fetch_unblocked_option_chain(symbol, expiry)
        
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
    """
    symbol = request.args.get("symbol", "NIFTY").upper()
    from_date = request.args.get("fromDate")
    to_date = request.args.get("toDate")
    expiry = request.args.get("expiry")
    
    if not from_date or not to_date:
        return jsonify({
            'success': False,
            'error': 'Missing date parameters'
        }), 400
    
    try:
        # Fetch historical data
        hist_data = _fetch_historical_data_raw(symbol, from_date, to_date, expiry)
        
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
            'rsi': analysis['rsi'],
            'historical_data': hist_data
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
    """
    symbol = request.args.get("symbol", "NIFTY").upper()
    expiry = request.args.get("expiry")
    
    try:
        # Fetch option chain
        option_chain_data = fetch_unblocked_option_chain(symbol, expiry)
        
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
    """
    symbol = request.args.get("symbol", "NIFTY").upper()
    expiry = request.args.get("expiry")
    
    try:
        # Fetch option chain
        option_chain_data = fetch_unblocked_option_chain(symbol, expiry)
        
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
