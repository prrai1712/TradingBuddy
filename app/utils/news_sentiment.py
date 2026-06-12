# app/utils/news_sentiment.py
"""
News Sentiment Analysis Module
Analyzes global and Indian market news for sentiment impact
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class NewsSentimentAnalyzer:
    """Analyze news sentiment from various sources"""
    
    def __init__(self):
        self.sentiment_keywords = {
            'positive': [
                'bullish', 'rally', 'surge', 'gain', 'rise', 'growth', 'profit', 
                'record', 'high', 'optimistic', 'upgrade', 'outperform', 'beat',
                'strong', 'recovery', 'boom', 'breakthrough', 'positive', 'upside'
            ],
            'negative': [
                'bearish', 'crash', 'plunge', 'fall', 'decline', 'loss', 'drop',
                'low', 'pessimistic', 'downgrade', 'underperform', 'miss',
                'weak', 'recession', 'slowdown', 'concern', 'negative', 'downside',
                'risk', 'warning', 'alert', 'crisis', 'fear'
            ],
            'market_moving': [
                'fed', 'rbi', 'inflation', 'interest rate', 'gdp', 'employment',
                'earnings', 'quarterly results', 'policy', 'election', 'war',
                'tension', 'conflict', 'trade', 'tariff', 'sanction', 'oil price',
                'crude', 'gold', 'dollar', 'rupee', 'forex', 'bond yield'
            ]
        }
    
    def analyze_text_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of a given text
        Returns sentiment score and classification
        """
        if not text:
            return {'score': 0, 'classification': 'NEUTRAL'}
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.sentiment_keywords['positive'] 
                           if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_keywords['negative'] 
                           if word in text_lower)
        market_moving_count = sum(1 for word in self.sentiment_keywords['market_moving'] 
                                 if word in text_lower)
        
        # Calculate sentiment score (-10 to +10)
        if positive_count + negative_count == 0:
            score = 0
        else:
            score = (positive_count - negative_count) / max(positive_count + negative_count, 1) * 10
        
        # Classify sentiment
        if score >= 3:
            classification = 'POSITIVE'
        elif score <= -3:
            classification = 'NEGATIVE'
        else:
            classification = 'NEUTRAL'
        
        # Determine market impact
        if market_moving_count >= 3:
            impact = 'HIGH'
        elif market_moving_count >= 1:
            impact = 'MEDIUM'
        else:
            impact = 'LOW'
        
        return {
            'score': round(score, 2),
            'classification': classification,
            'positive_mentions': positive_count,
            'negative_mentions': negative_count,
            'market_moving_mentions': market_moving_count,
            'impact': impact
        }
    
    def fetch_global_news(self) -> List[Dict]:
        """
        Fetch global market news (simulated - in production would use news API)
        """
        # In production, integrate with:
        # - NewsAPI.org
        # - Bloomberg API
        # - Reuters API
        # - Alpha Vantage News Sentiment
        
        # For now, return placeholder structure
        return [
            {
                'source': 'Global Markets',
                'headline': 'US Markets close mixed amid Fed policy uncertainty',
                'summary': 'Major US indices showed mixed performance as investors await Federal Reserve policy decision.',
                'timestamp': datetime.now().isoformat(),
                'region': 'US'
            },
            {
                'source': 'Asian Markets',
                'headline': 'Asian stocks rise on tech sector strength',
                'summary': 'Asian equity markets gained ground led by technology stocks.',
                'timestamp': datetime.now().isoformat(),
                'region': 'ASIA'
            },
            {
                'source': 'Commodities',
                'headline': 'Oil prices stabilize after recent volatility',
                'summary': 'Crude oil prices found stability after sharp movements earlier in the week.',
                'timestamp': datetime.now().isoformat(),
                'region': 'GLOBAL'
            }
        ]
    
    def fetch_indian_news(self) -> List[Dict]:
        """
        Fetch Indian market news (simulated - in production would use news API)
        """
        # In production, integrate with:
        # - Moneycontrol API
        # - Economic Times API
        # - Business Standard API
        # - NSE/BSE announcements
        
        return [
            {
                'source': 'Indian Markets',
                'headline': 'Nifty reaches new high on strong FII inflows',
                'summary': 'Indian benchmark index touched fresh peaks driven by foreign investor buying.',
                'timestamp': datetime.now().isoformat(),
                'region': 'INDIA'
            },
            {
                'source': 'RBI Policy',
                'headline': 'RBI maintains repo rate unchanged',
                'summary': 'Reserve Bank of India kept key interest rates steady citing inflation concerns.',
                'timestamp': datetime.now().isoformat(),
                'region': 'INDIA'
            },
            {
                'source': 'Corporate',
                'headline': 'IT stocks gain on strong quarterly earnings',
                'summary': 'Information technology stocks rallied after better-than-expected results.',
                'timestamp': datetime.now().isoformat(),
                'region': 'INDIA'
            }
        ]
    
    def analyze_global_sentiment(self) -> Dict:
        """
        Analyze overall global market sentiment
        """
        news_items = self.fetch_global_news()
        
        scores = []
        classifications = []
        
        for news in news_items:
            combined_text = f"{news.get('headline', '')} {news.get('summary', '')}"
            sentiment = self.analyze_text_sentiment(combined_text)
            scores.append(sentiment['score'])
            classifications.append(sentiment['classification'])
            
            # Add sentiment back to news item
            news['sentiment'] = sentiment
        
        # Calculate composite score
        composite_score = sum(scores) / len(scores) if scores else 0
        
        # Count classifications
        positive_count = classifications.count('POSITIVE')
        negative_count = classifications.count('NEGATIVE')
        neutral_count = classifications.count('NEUTRAL')
        
        # Overall classification
        if positive_count > negative_count:
            overall = 'POSITIVE'
        elif negative_count > positive_count:
            overall = 'NEGATIVE'
        else:
            overall = 'NEUTRAL'
        
        return {
            'composite_score': round(composite_score, 2),
            'overall_classification': overall,
            'news_count': len(news_items),
            'positive_news': positive_count,
            'negative_news': negative_count,
            'neutral_news': neutral_count,
            'news_items': news_items
        }
    
    def analyze_indian_sentiment(self) -> Dict:
        """
        Analyze overall Indian market sentiment
        """
        news_items = self.fetch_indian_news()
        
        scores = []
        classifications = []
        
        for news in news_items:
            combined_text = f"{news.get('headline', '')} {news.get('summary', '')}"
            sentiment = self.analyze_text_sentiment(combined_text)
            scores.append(sentiment['score'])
            classifications.append(sentiment['classification'])
            
            # Add sentiment back to news item
            news['sentiment'] = sentiment
        
        # Calculate composite score
        composite_score = sum(scores) / len(scores) if scores else 0
        
        # Count classifications
        positive_count = classifications.count('POSITIVE')
        negative_count = classifications.count('NEGATIVE')
        neutral_count = classifications.count('NEUTRAL')
        
        # Overall classification
        if positive_count > negative_count:
            overall = 'POSITIVE'
        elif negative_count > positive_count:
            overall = 'NEGATIVE'
        else:
            overall = 'NEUTRAL'
        
        return {
            'composite_score': round(composite_score, 2),
            'overall_classification': overall,
            'news_count': len(news_items),
            'positive_news': positive_count,
            'negative_news': negative_count,
            'neutral_news': neutral_count,
            'news_items': news_items
        }
    
    def get_combined_market_sentiment(self) -> Dict:
        """
        Get combined global and Indian market sentiment
        """
        global_sentiment = self.analyze_global_sentiment()
        indian_sentiment = self.analyze_indian_sentiment()
        
        # Weighted average (Indian market gets higher weight for Indian stocks)
        combined_score = (global_sentiment['composite_score'] * 0.4 + 
                         indian_sentiment['composite_score'] * 0.6)
        
        # Determine overall market bias
        if combined_score >= 3:
            market_bias = 'BULLISH'
        elif combined_score <= -3:
            market_bias = 'BEARISH'
        else:
            market_bias = 'NEUTRAL'
        
        # Confidence level
        total_news = global_sentiment['news_count'] + indian_sentiment['news_count']
        if total_news >= 10:
            confidence = 'HIGH'
        elif total_news >= 5:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        return {
            'timestamp': datetime.now().isoformat(),
            'combined_score': round(combined_score, 2),
            'market_bias': market_bias,
            'confidence': confidence,
            'global_sentiment': global_sentiment,
            'indian_sentiment': indian_sentiment,
            'key_factors': self._identify_key_factors(global_sentiment, indian_sentiment)
        }
    
    def _identify_key_factors(self, global_sentiment: Dict, indian_sentiment: Dict) -> List[str]:
        """Identify key factors affecting market sentiment"""
        factors = []
        
        # Check global factors
        if global_sentiment['negative_news'] > global_sentiment['positive_news']:
            factors.append('Negative global sentiment')
        if global_sentiment['positive_news'] > global_sentiment['negative_news']:
            factors.append('Positive global sentiment')
        
        # Check Indian factors
        if indian_sentiment['negative_news'] > indian_sentiment['positive_news']:
            factors.append('Negative domestic sentiment')
        if indian_sentiment['positive_news'] > indian_sentiment['negative_news']:
            factors.append('Positive domestic sentiment')
        
        # Check for specific themes
        for news in global_sentiment.get('news_items', []) + indian_sentiment.get('news_items', []):
            headline = news.get('headline', '').lower()
            if 'fed' in headline or 'rate' in headline:
                factors.append('Central bank policy in focus')
                break
            if 'oil' in headline or 'crude' in headline:
                factors.append('Oil price volatility')
                break
            if 'earnings' in headline or 'results' in headline:
                factors.append('Earnings season impact')
                break
        
        return list(set(factors))[:5]  # Return top 5 unique factors


def get_market_sentiment_report() -> Dict:
    """
    Main function to get complete market sentiment report
    """
    analyzer = NewsSentimentAnalyzer()
    return analyzer.get_combined_market_sentiment()
