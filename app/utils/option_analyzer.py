# app/utils/option_analyzer.py
"""
Advanced Option Chain Analysis Module
Performs deep calculations and analysis on option chain data
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class OptionChainAnalyzer:
    """Deep analysis of option chain data with multiple indicators"""
    
    def __init__(self, option_chain_data: Dict):
        self.data = option_chain_data
        self.records = option_chain_data.get('records', {})
        self.strike_data = self.records.get('strikeData', [])
        self.underlying_value = self.records.get('underlyingValue', 0)
        
    def calculate_pcr(self) -> Dict[str, float]:
        """
        Calculate Put-Call Ratio (PCR) for OI and Volume
        Returns overall PCR and per-strike PCR
        """
        total_call_oi = 0
        total_put_oi = 0
        total_call_volume = 0
        total_put_volume = 0
        
        strike_pcr = []
        
        for strike in self.strike_data:
            ce = strike.get('CE', {})
            pe = strike.get('PE', {})
            
            call_oi = ce.get('openInterest', 0) or 0
            put_oi = pe.get('openInterest', 0) or 0
            call_vol = ce.get('totalTradedVolume', 0) or 0
            put_vol = pe.get('totalTradedVolume', 0) or 0
            
            total_call_oi += call_oi
            total_put_oi += put_oi
            total_call_volume += call_vol
            total_put_volume += put_vol
            
            # Per-strike PCR
            if call_oi > 0:
                strike_pcr.append({
                    'strike': strike.get('strikePrice', 0),
                    'oi_pcr': round(put_oi / call_oi, 2) if call_oi > 0 else 0,
                    'volume_pcr': round(put_vol / call_vol, 2) if call_vol > 0 else 0
                })
        
        overall_oi_pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 0
        overall_volume_pcr = round(total_put_volume / total_call_volume, 2) if total_call_volume > 0 else 0
        
        return {
            'overall_oi_pcr': overall_oi_pcr,
            'overall_volume_pcr': overall_volume_pcr,
            'strike_wise_pcr': strike_pcr,
            'total_call_oi': total_call_oi,
            'total_put_oi': total_put_oi,
            'total_call_volume': total_call_volume,
            'total_put_volume': total_put_volume
        }
    
    def find_max_pain(self) -> Dict:
        """
        Calculate Max Pain point - the strike where option writers have minimum loss
        """
        if not self.strike_data:
            return {'max_pain_strike': 0, 'total_pain': 0}
        
        pain_calculations = []
        
        for strike in self.strike_data:
            strike_price = strike.get('strikePrice', 0)
            ce = strike.get('CE', {})
            pe = strike.get('PE', {})
            
            call_oi = ce.get('openInterest', 0) or 0
            put_oi = pe.get('openInterest', 0) or 0
            
            # Calculate pain at this strike
            call_pain = max(0, self.underlying_value - strike_price) * call_oi
            put_pain = max(0, strike_price - self.underlying_value) * put_oi
            total_pain = call_pain + put_pain
            
            pain_calculations.append({
                'strike': strike_price,
                'total_pain': total_pain,
                'call_pain': call_pain,
                'put_pain': put_pain
            })
        
        # Find strike with minimum pain
        min_pain = min(pain_calculations, key=lambda x: x['total_pain'])
        
        return {
            'max_pain_strike': min_pain['strike'],
            'total_pain': min_pain['total_pain'],
            'all_pain_points': sorted(pain_calculations, key=lambda x: x['total_pain'])[:5]
        }
    
    def calculate_greeks_approximation(self) -> Dict:
        """
        Approximate Greeks calculation for ATM options
        Using simplified Black-Scholes approximations
        """
        atm_strike = min(self.strike_data, 
                        key=lambda x: abs(x.get('strikePrice', 0) - self.underlying_value))
        
        ce = atm_strike.get('CE', {})
        pe = atm_strike.get('PE', {})
        
        call_ltp = ce.get('lastPrice', 0) or 0
        put_ltp = pe.get('lastPrice', 0) or 0
        call_oi_change = ce.get('changeinOI', 0) or 0
        put_oi_change = pe.get('changeinOI', 0) or 0
        call_vol = ce.get('totalTradedVolume', 0) or 0
        put_vol = pe.get('totalTradedVolume', 0) or 0
        
        # Implied volatility approximation (simplified)
        time_to_expiry = 7  # Assume 7 days to expiry
        risk_free_rate = 0.065  # 6.5% annual
        
        # Simple IV estimation from option price
        intrinsic_call = max(0, self.underlying_value - atm_strike.get('strikePrice', 0))
        time_value_call = max(0.01, call_ltp - intrinsic_call)
        
        iv_approx = (time_value_call / self.underlying_value) * math.sqrt(252 / time_to_expiry) * 100
        
        return {
            'atm_strike': atm_strike.get('strikePrice', 0),
            'call_ltp': call_ltp,
            'put_ltp': put_ltp,
            'estimated_iv': round(iv_approx, 2),
            'call_oi_change': call_oi_change,
            'put_oi_change': put_oi_change,
            'call_volume': call_vol,
            'put_volume': put_vol,
            'put_call_ratio': round(put_ltp / call_ltp, 2) if call_ltp > 0 else 0
        }
    
    def identify_support_resistance(self) -> Dict:
        """
        Identify support and resistance levels from option chain
        Based on highest OI concentrations
        """
        call_oi_strikes = []
        put_oi_strikes = []
        
        for strike in self.strike_data:
            ce = strike.get('CE', {})
            pe = strike.get('PE', {})
            
            call_oi = ce.get('openInterest', 0) or 0
            put_oi = pe.get('openInterest', 0) or 0
            
            call_oi_strikes.append({'strike': strike.get('strikePrice', 0), 'oi': call_oi})
            put_oi_strikes.append({'strike': strike.get('strikePrice', 0), 'oi': put_oi})
        
        # Sort by OI descending
        call_oi_strikes.sort(key=lambda x: x['oi'], reverse=True)
        put_oi_strikes.sort(key=lambda x: x['oi'], reverse=True)
        
        # Top resistance (highest call OI above spot)
        resistance_levels = [
            s for s in call_oi_strikes 
            if s['strike'] > self.underlying_value
        ][:3]
        
        # Top support (highest put OI below spot)
        support_levels = [
            s for s in put_oi_strikes 
            if s['strike'] < self.underlying_value
        ][:3]
        
        return {
            'resistance_levels': resistance_levels,
            'support_levels': support_levels,
            'strongest_resistance': resistance_levels[0] if resistance_levels else None,
            'strongest_support': support_levels[0] if support_levels else None
        }
    
    def analyze_oi_buildup(self) -> Dict:
        """
        Analyze Open Interest buildup patterns
        Identifies long buildup, short buildup, long unwinding, short covering
        """
        patterns = {
            'long_buildup': [],      # Price ↑, OI ↑
            'short_buildup': [],     # Price ↓, OI ↑
            'long_unwinding': [],    # Price ↓, OI ↓
            'short_covering': []     # Price ↑, OI ↓
        }
        
        for strike in self.strike_data:
            ce = strike.get('CE', {})
            pe = strike.get('PE', {})
            
            strike_price = strike.get('strikePrice', 0)
            
            # Call analysis
            call_price_change = ce.get('pChange', 0) or 0
            call_oi_change_pct = ce.get('pchgopeninterest', 0) or 0
            call_oi = ce.get('openInterest', 0) or 0
            
            if call_oi > 1000:  # Minimum OI threshold
                if call_price_change > 2 and call_oi_change_pct > 5:
                    patterns['long_buildup'].append({
                        'strike': strike_price, 'type': 'CE',
                        'price_change': call_price_change, 'oi_change_pct': call_oi_change_pct
                    })
                elif call_price_change < -2 and call_oi_change_pct > 5:
                    patterns['short_buildup'].append({
                        'strike': strike_price, 'type': 'CE',
                        'price_change': call_price_change, 'oi_change_pct': call_oi_change_pct
                    })
                elif call_price_change < -2 and call_oi_change_pct < -5:
                    patterns['long_unwinding'].append({
                        'strike': strike_price, 'type': 'CE',
                        'price_change': call_price_change, 'oi_change_pct': call_oi_change_pct
                    })
                elif call_price_change > 2 and call_oi_change_pct < -5:
                    patterns['short_covering'].append({
                        'strike': strike_price, 'type': 'CE',
                        'price_change': call_price_change, 'oi_change_pct': call_oi_change_pct
                    })
            
            # Put analysis
            put_price_change = pe.get('pChange', 0) or 0
            put_oi_change_pct = pe.get('pchgopeninterest', 0) or 0
            put_oi = pe.get('openInterest', 0) or 0
            
            if put_oi > 1000:
                if put_price_change > 2 and put_oi_change_pct > 5:
                    patterns['long_buildup'].append({
                        'strike': strike_price, 'type': 'PE',
                        'price_change': put_price_change, 'oi_change_pct': put_oi_change_pct
                    })
                elif put_price_change < -2 and put_oi_change_pct > 5:
                    patterns['short_buildup'].append({
                        'strike': strike_price, 'type': 'PE',
                        'price_change': put_price_change, 'oi_change_pct': put_oi_change_pct
                    })
                elif put_price_change < -2 and put_oi_change_pct < -5:
                    patterns['long_unwinding'].append({
                        'strike': strike_price, 'type': 'PE',
                        'price_change': put_price_change, 'oi_change_pct': put_oi_change_pct
                    })
                elif put_price_change > 2 and put_oi_change_pct < -5:
                    patterns['short_covering'].append({
                        'strike': strike_price, 'type': 'PE',
                        'price_change': put_price_change, 'oi_change_pct': put_oi_change_pct
                    })
        
        return patterns
    
    def get_comprehensive_analysis(self) -> Dict:
        """
        Run all analyses and return comprehensive report
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'underlying_value': self.underlying_value,
            'pcr_analysis': self.calculate_pcr(),
            'max_pain': self.find_max_pain(),
            'greeks_approx': self.calculate_greeks_approximation(),
            'support_resistance': self.identify_support_resistance(),
            'oi_buildup': self.analyze_oi_buildup()
        }


class HistoricalPatternAnalyzer:
    """Analyze historical price patterns for prediction"""
    
    def __init__(self, historical_data: List[Dict]):
        self.data = historical_data
        
    def calculate_moving_averages(self) -> Dict:
        """Calculate SMA and EMA for various periods"""
        if len(self.data) < 200:
            return {'error': 'Insufficient data'}
        
        closes = [d.get('close', 0) for d in self.data if d.get('close')]
        
        def sma(period):
            if len(closes) < period:
                return None
            return round(sum(closes[-period:]) / period, 2)
        
        def ema(period):
            if len(closes) < period:
                return None
            multiplier = 2 / (period + 1)
            ema_val = sum(closes[:period]) / period
            for close in closes[period:]:
                ema_val = (close * multiplier) + (ema_val * (1 - multiplier))
            return round(ema_val, 2)
        
        return {
            'sma_20': sma(20),
            'sma_50': sma(50),
            'sma_200': sma(200),
            'ema_9': ema(9),
            'ema_21': ema(21),
            'current_price': closes[-1] if closes else 0
        }
    
    def detect_trend(self) -> str:
        """Detect current trend direction"""
        ma = self.calculate_moving_averages()
        
        if ma.get('error'):
            return 'UNKNOWN'
        
        current = ma.get('current_price', 0)
        sma_20 = ma.get('sma_20', 0)
        sma_50 = ma.get('sma_50', 0)
        sma_200 = ma.get('sma_200', 0)
        
        if current > sma_20 > sma_50 > sma_200:
            return 'STRONG_UPTREND'
        elif current > sma_20 > sma_50:
            return 'UPTREND'
        elif current < sma_20 < sma_50 < sma_200:
            return 'STRONG_DOWNTREND'
        elif current < sma_20 < sma_50:
            return 'DOWNTREND'
        else:
            return 'SIDEWAYS'
    
    def find_patterns(self) -> List[Dict]:
        """Find common candlestick patterns in recent data"""
        patterns = []
        
        if len(self.data) < 10:
            return patterns
        
        recent = self.data[-10:]
        
        # Check for doji, hammer, engulfing patterns (simplified)
        for i in range(1, len(recent)):
            curr = recent[i]
            prev = recent[i-1]
            
            curr_open = curr.get('open', 0)
            curr_close = curr.get('close', 0)
            curr_high = curr.get('high', 0)
            curr_low = curr.get('low', 0)
            
            prev_open = prev.get('open', 0)
            prev_close = prev.get('close', 0)
            
            body = abs(curr_close - curr_open)
            range_size = curr_high - curr_low
            
            # Doji pattern
            if range_size > 0 and body / range_size < 0.1:
                patterns.append({
                    'pattern': 'DOJI',
                    'date': curr.get('date'),
                    'significance': 'INDECISION'
                })
            
            # Bullish engulfing
            if (curr_close > curr_open and prev_close < prev_open and
                curr_open < prev_close and curr_close > prev_open):
                patterns.append({
                    'pattern': 'BULLISH_ENGULFING',
                    'date': curr.get('date'),
                    'significance': 'BULLISH'
                })
            
            # Bearish engulfing
            if (curr_close < curr_open and prev_close > prev_open and
                curr_open > prev_close and curr_close < prev_open):
                patterns.append({
                    'pattern': 'BEARISH_ENGULFING',
                    'date': curr.get('date'),
                    'significance': 'BEARISH'
                })
        
        return patterns
    
    def calculate_rsi(self, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(self.data) < period + 1:
            return 50.0
        
        closes = [d.get('close', 0) for d in self.data if d.get('close')]
        
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def get_historical_analysis(self) -> Dict:
        """Complete historical analysis"""
        return {
            'moving_averages': self.calculate_moving_averages(),
            'trend': self.detect_trend(),
            'patterns': self.find_patterns(),
            'rsi': self.calculate_rsi(),
            'data_points': len(self.data)
        }


class SentimentAnalyzer:
    """Analyze market sentiment from various factors"""
    
    def __init__(self, 
                 pcr_data: Dict, 
                 historical_data: Dict,
                 global_sentiment: Optional[Dict] = None):
        self.pcr = pcr_data
        self.historical = historical_data
        self.global_sentiment = global_sentiment or {}
    
    def calculate_sentiment_score(self) -> Dict:
        """
        Calculate overall market sentiment score (-100 to +100)
        Negative = Bearish, Positive = Bullish
        """
        score = 0
        factors = []
        
        # PCR Analysis (weight: 30%)
        oi_pcr = self.pcr.get('overall_oi_pcr', 1)
        if oi_pcr > 1.2:
            score += 25
            factors.append({'factor': 'High PCR', 'impact': '+25', 'signal': 'BULLISH'})
        elif oi_pcr > 1.0:
            score += 10
            factors.append({'factor': 'PCR > 1', 'impact': '+10', 'signal': 'BULLISH'})
        elif oi_pcr < 0.8:
            score -= 25
            factors.append({'factor': 'Low PCR', 'impact': '-25', 'signal': 'BEARISH'})
        elif oi_pcr < 1.0:
            score -= 10
            factors.append({'factor': 'PCR < 1', 'impact': '-10', 'signal': 'BEARISH'})
        
        # RSI Analysis (weight: 20%)
        rsi = self.historical.get('rsi', 50)
        if rsi > 70:
            score -= 15
            factors.append({'factor': 'Overbought RSI', 'impact': '-15', 'signal': 'BEARISH'})
        elif rsi < 30:
            score += 15
            factors.append({'factor': 'Oversold RSI', 'impact': '+15', 'signal': 'BULLISH'})
        elif rsi > 60:
            score += 5
            factors.append({'factor': 'Strong RSI', 'impact': '+5', 'signal': 'BULLISH'})
        elif rsi < 40:
            score -= 5
            factors.append({'factor': 'Weak RSI', 'impact': '-5', 'signal': 'BEARISH'})
        
        # Trend Analysis (weight: 30%)
        trend = self.historical.get('trend', 'SIDEWAYS')
        trend_scores = {
            'STRONG_UPTREND': 30,
            'UPTREND': 20,
            'SIDEWAYS': 0,
            'DOWNTREND': -20,
            'STRONG_DOWNTREND': -30
        }
        trend_score = trend_scores.get(trend, 0)
        score += trend_score
        factors.append({'factor': f'Trend: {trend}', 'impact': str(trend_score), 
                       'signal': 'BULLISH' if trend_score > 0 else 'BEARISH' if trend_score < 0 else 'NEUTRAL'})
        
        # Global Sentiment (weight: 20%)
        if self.global_sentiment:
            global_score = self.global_sentiment.get('composite_score', 0)
            adjusted_global = global_score * 0.2
            score += adjusted_global
            factors.append({'factor': 'Global Sentiment', 'impact': str(round(adjusted_global, 1)),
                           'signal': 'BULLISH' if adjusted_global > 0 else 'BEARISH' if adjusted_global < 0 else 'NEUTRAL'})
        
        # Cap score between -100 and 100
        score = max(-100, min(100, score))
        
        # Determine signal
        if score >= 40:
            signal = 'STRONG_BUY'
        elif score >= 20:
            signal = 'BUY'
        elif score >= -20:
            signal = 'NEUTRAL'
        elif score >= -40:
            signal = 'SELL'
        else:
            signal = 'STRONG_SELL'
        
        return {
            'sentiment_score': round(score, 2),
            'signal': signal,
            'factors': factors,
            'confidence': 'HIGH' if abs(score) > 60 else 'MEDIUM' if abs(score) > 30 else 'LOW'
        }


def generate_trading_signal(option_chain: Dict, 
                           historical_data: List[Dict],
                           global_sentiment: Optional[Dict] = None) -> Dict:
    """
    Main function to generate CALL/PUT trading signal
    Combines all analyses for final recommendation
    """
    # Initialize analyzers
    option_analyzer = OptionChainAnalyzer(option_chain)
    historical_analyzer = HistoricalPatternAnalyzer(historical_data)
    
    # Run analyses
    option_analysis = option_analyzer.get_comprehensive_analysis()
    historical_analysis = historical_analyzer.get_historical_analysis()
    
    # Calculate sentiment
    sentiment_analyzer = SentimentAnalyzer(
        option_analysis['pcr_analysis'],
        historical_analysis,
        global_sentiment
    )
    sentiment_result = sentiment_analyzer.calculate_sentiment_score()
    
    # Generate final signal
    score = sentiment_result['sentiment_score']
    
    if score >= 30:
        primary_signal = 'CALL'
        confidence = 'HIGH' if score >= 50 else 'MEDIUM'
    elif score <= -30:
        primary_signal = 'PUT'
        confidence = 'HIGH' if score <= -50 else 'MEDIUM'
    else:
        primary_signal = 'NO_TRADE'
        confidence = 'LOW'
    
    # Determine strike recommendations
    atm_strike = option_analysis['greeks_approx'].get('atm_strike', 0)
    max_pain = option_analysis['max_pain'].get('max_pain_strike', 0)
    support = option_analysis['support_resistance'].get('strongest_support', {})
    resistance = option_analysis['support_resistance'].get('strongest_resistance', {})
    
    recommended_strikes = []
    if primary_signal == 'CALL':
        if support.get('strike'):
            recommended_strikes.append({
                'type': 'ITM_CALL',
                'strike': support.get('strike'),
                'reason': 'Support level - safer play'
            })
        if atm_strike:
            recommended_strikes.append({
                'type': 'ATM_CALL',
                'strike': atm_strike,
                'reason': 'At-the-money - balanced risk/reward'
            })
    elif primary_signal == 'PUT':
        if resistance.get('strike'):
            recommended_strikes.append({
                'type': 'ITM_PUT',
                'strike': resistance.get('strike'),
                'reason': 'Resistance level - safer play'
            })
        if atm_strike:
            recommended_strikes.append({
                'type': 'ATM_PUT',
                'strike': atm_strike,
                'reason': 'At-the-money - balanced risk/reward'
            })
    
    return {
        'timestamp': datetime.now().isoformat(),
        'signal': primary_signal,
        'confidence': confidence,
        'sentiment_score': score,
        'underlying_value': option_analysis['underlying_value'],
        'recommended_strikes': recommended_strikes,
        'key_levels': {
            'support': support.get('strike') if support else None,
            'resistance': resistance.get('strike') if resistance else None,
            'max_pain': max_pain
        },
        'analysis_summary': {
            'pcr': option_analysis['pcr_analysis']['overall_oi_pcr'],
            'trend': historical_analysis['trend'],
            'rsi': historical_analysis['rsi'],
            'patterns_detected': len(historical_analysis['patterns'])
        },
        'risk_factors': sentiment_result['factors'],
        'full_analysis': {
            'option_chain': option_analysis,
            'historical': historical_analysis,
            'sentiment': sentiment_result
        }
    }
