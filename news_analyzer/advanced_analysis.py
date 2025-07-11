#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 분석 기능
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import logging
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)

class AdvancedAnalyzer:
    """고급 분석기"""
    
    def __init__(self):
        self.analysis_history = []
        self.pattern_detector = PatternDetector()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
    
    def analyze_market_sentiment_trend(self, news_data: List[Dict]) -> Dict[str, Any]:
        """시장 감정 트렌드 분석"""
        try:
            # 시간별 감정 분포 분석
            time_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
            
            for news in news_data:
                if 'published' in news and 'sentiment' in news:
                    date = news['published'].date()
                    sentiment = news['sentiment'].get('label', 'neutral')
                    time_sentiment[date][sentiment] += 1
            
            # 감정 지수 계산
            sentiment_index = {}
            for date, counts in time_sentiment.items():
                total = sum(counts.values())
                if total > 0:
                    positive_ratio = counts['positive'] / total
                    negative_ratio = counts['negative'] / total
                    sentiment_index[date] = positive_ratio - negative_ratio
            
            # 트렌드 분석
            trend_analysis = self.trend_analyzer.analyze_sentiment_trend(sentiment_index)
            
            return {
                "sentiment_index": sentiment_index,
                "trend_analysis": trend_analysis,
                "total_news": len(news_data),
                "date_range": {
                    "start": min(time_sentiment.keys()) if time_sentiment else None,
                    "end": max(time_sentiment.keys()) if time_sentiment else None
                }
            }
        except Exception as e:
            logger.error(f"시장 감정 트렌드 분석 실패: {e}")
            return {}
    
    def analyze_sector_performance(self, news_data: List[Dict]) -> Dict[str, Any]:
        """업종별 성과 분석"""
        try:
            sector_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
            sector_news_count = defaultdict(int)
            
            for news in news_data:
                if 'related_stocks' in news:
                    for stock in news['related_stocks']:
                        sector = stock.get('sector', '기타')
                        sentiment = news.get('sentiment', {}).get('label', 'neutral')
                        sector_sentiment[sector][sentiment] += 1
                        sector_news_count[sector] += 1
            
            # 업종별 성과 점수 계산
            sector_performance = {}
            for sector, counts in sector_sentiment.items():
                total = sum(counts.values())
                if total > 0:
                    positive_ratio = counts['positive'] / total
                    negative_ratio = counts['negative'] / total
                    performance_score = positive_ratio - negative_ratio
                    sector_performance[sector] = {
                        'performance_score': performance_score,
                        'news_count': sector_news_count[sector],
                        'sentiment_distribution': counts
                    }
            
            return {
                "sector_performance": sector_performance,
                "top_performing_sectors": sorted(
                    sector_performance.items(),
                    key=lambda x: x[1]['performance_score'],
                    reverse=True
                )[:5],
                "total_sectors": len(sector_performance)
            }
        except Exception as e:
            logger.error(f"업종별 성과 분석 실패: {e}")
            return {}
    
    def detect_market_patterns(self, news_data: List[Dict]) -> Dict[str, Any]:
        """시장 패턴 탐지"""
        try:
            patterns = self.pattern_detector.detect_patterns(news_data)
            return patterns
        except Exception as e:
            logger.error(f"시장 패턴 탐지 실패: {e}")
            return {}
    
    def analyze_correlation(self, news_data: List[Dict]) -> Dict[str, Any]:
        """상관관계 분석"""
        try:
            correlations = self.correlation_analyzer.analyze_correlations(news_data)
            return correlations
        except Exception as e:
            logger.error(f"상관관계 분석 실패: {e}")
            return {}

class PatternDetector:
    """패턴 탐지기"""
    
    def __init__(self):
        self.patterns = {
            'momentum': self._detect_momentum_pattern,
            'reversal': self._detect_reversal_pattern,
            'consolidation': self._detect_consolidation_pattern,
            'breakout': self._detect_breakout_pattern
        }
    
    def detect_patterns(self, news_data: List[Dict]) -> Dict[str, Any]:
        """패턴 탐지"""
        detected_patterns = {}
        
        for pattern_name, detector_func in self.patterns.items():
            try:
                pattern_result = detector_func(news_data)
                if pattern_result:
                    detected_patterns[pattern_name] = pattern_result
            except Exception as e:
                logger.warning(f"패턴 탐지 실패 ({pattern_name}): {e}")
        
        return {
            "detected_patterns": detected_patterns,
            "pattern_count": len(detected_patterns)
        }
    
    def _detect_momentum_pattern(self, news_data: List[Dict]) -> Dict[str, Any]:
        """모멘텀 패턴 탐지"""
        # 긍정적 뉴스가 연속적으로 나타나는 패턴
        positive_streak = 0
        max_streak = 0
        
        for news in sorted(news_data, key=lambda x: x.get('published', datetime.now())):
            sentiment = news.get('sentiment', {}).get('label', 'neutral')
            if sentiment == 'positive':
                positive_streak += 1
                max_streak = max(max_streak, positive_streak)
            else:
                positive_streak = 0
        
        if max_streak >= 3:
            return {
                "type": "momentum",
                "strength": max_streak,
                "confidence": min(max_streak / 5, 1.0)
            }
        return None
    
    def _detect_reversal_pattern(self, news_data: List[Dict]) -> Dict[str, Any]:
        """반전 패턴 탐지"""
        # 긍정에서 부정으로 또는 부정에서 긍정으로의 전환
        sentiment_changes = []
        prev_sentiment = None
        
        for news in sorted(news_data, key=lambda x: x.get('published', datetime.now())):
            sentiment = news.get('sentiment', {}).get('label', 'neutral')
            if prev_sentiment and prev_sentiment != sentiment:
                sentiment_changes.append((prev_sentiment, sentiment))
            prev_sentiment = sentiment
        
        if len(sentiment_changes) >= 2:
            return {
                "type": "reversal",
                "changes": sentiment_changes,
                "confidence": min(len(sentiment_changes) / 5, 1.0)
            }
        return None
    
    def _detect_consolidation_pattern(self, news_data: List[Dict]) -> Dict[str, Any]:
        """통합 패턴 탐지"""
        # 중립적 뉴스가 지속되는 패턴
        neutral_count = sum(1 for news in news_data 
                          if news.get('sentiment', {}).get('label') == 'neutral')
        
        if neutral_count >= len(news_data) * 0.6:
            return {
                "type": "consolidation",
                "neutral_ratio": neutral_count / len(news_data),
                "confidence": neutral_count / len(news_data)
            }
        return None
    
    def _detect_breakout_pattern(self, news_data: List[Dict]) -> Dict[str, Any]:
        """돌파 패턴 탐지"""
        # 급격한 감정 변화 패턴
        sentiment_scores = []
        for news in sorted(news_data, key=lambda x: x.get('published', datetime.now())):
            sentiment = news.get('sentiment', {}).get('label', 'neutral')
            score = 1 if sentiment == 'positive' else (-1 if sentiment == 'negative' else 0)
            sentiment_scores.append(score)
        
        if len(sentiment_scores) >= 3:
            # 급격한 변화 탐지
            changes = [abs(sentiment_scores[i] - sentiment_scores[i-1]) 
                      for i in range(1, len(sentiment_scores))]
            max_change = max(changes)
            
            if max_change >= 2:  # 급격한 변화
                return {
                    "type": "breakout",
                    "max_change": max_change,
                    "confidence": min(max_change / 3, 1.0)
                }
        return None

class CorrelationAnalyzer:
    """상관관계 분석기"""
    
    def __init__(self):
        self.correlation_methods = {
            'sentiment_keyword': self._analyze_sentiment_keyword_correlation,
            'sector_sentiment': self._analyze_sector_sentiment_correlation,
            'time_sentiment': self._analyze_time_sentiment_correlation
        }
    
    def analyze_correlations(self, news_data: List[Dict]) -> Dict[str, Any]:
        """상관관계 분석"""
        correlations = {}
        
        for method_name, method_func in self.correlation_methods.items():
            try:
                correlation_result = method_func(news_data)
                if correlation_result:
                    correlations[method_name] = correlation_result
            except Exception as e:
                logger.warning(f"상관관계 분석 실패 ({method_name}): {e}")
        
        return correlations
    
    def _analyze_sentiment_keyword_correlation(self, news_data: List[Dict]) -> Dict[str, Any]:
        """감정-키워드 상관관계 분석"""
        keyword_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
        
        for news in news_data:
            sentiment = news.get('sentiment', {}).get('label', 'neutral')
            keywords = news.get('financial_keywords', {}).get('stock_keywords', [])
            
            for keyword in keywords:
                keyword_sentiment[keyword][sentiment] += 1
        
        # 상관관계 계산
        correlations = {}
        for keyword, counts in keyword_sentiment.items():
            total = sum(counts.values())
            if total >= 3:  # 최소 3번 이상 등장한 키워드만
                positive_ratio = counts['positive'] / total
                negative_ratio = counts['negative'] / total
                correlation = positive_ratio - negative_ratio
                correlations[keyword] = {
                    'correlation': correlation,
                    'frequency': total,
                    'sentiment_distribution': counts
                }
        
        return {
            "keyword_correlations": correlations,
            "top_correlated_keywords": sorted(
                correlations.items(),
                key=lambda x: abs(x[1]['correlation']),
                reverse=True
            )[:10]
        }
    
    def _analyze_sector_sentiment_correlation(self, news_data: List[Dict]) -> Dict[str, Any]:
        """업종-감정 상관관계 분석"""
        sector_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
        
        for news in news_data:
            sentiment = news.get('sentiment', {}).get('label', 'neutral')
            stocks = news.get('related_stocks', [])
            
            for stock in stocks:
                sector = stock.get('sector', '기타')
                sector_sentiment[sector][sentiment] += 1
        
        # 상관관계 계산
        correlations = {}
        for sector, counts in sector_sentiment.items():
            total = sum(counts.values())
            if total >= 2:  # 최소 2번 이상 등장한 업종만
                positive_ratio = counts['positive'] / total
                negative_ratio = counts['negative'] / total
                correlation = positive_ratio - negative_ratio
                correlations[sector] = {
                    'correlation': correlation,
                    'frequency': total,
                    'sentiment_distribution': counts
                }
        
        return {
            "sector_correlations": correlations,
            "top_correlated_sectors": sorted(
                correlations.items(),
                key=lambda x: abs(x[1]['correlation']),
                reverse=True
            )[:10]
        }
    
    def _analyze_time_sentiment_correlation(self, news_data: List[Dict]) -> Dict[str, Any]:
        """시간-감정 상관관계 분석"""
        hourly_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
        
        for news in news_data:
            if 'published' in news:
                hour = news['published'].hour
                sentiment = news.get('sentiment', {}).get('label', 'neutral')
                hourly_sentiment[hour][sentiment] += 1
        
        # 시간대별 감정 패턴 분석
        time_patterns = {}
        for hour, counts in hourly_sentiment.items():
            total = sum(counts.values())
            if total > 0:
                positive_ratio = counts['positive'] / total
                negative_ratio = counts['negative'] / total
                time_patterns[hour] = {
                    'positive_ratio': positive_ratio,
                    'negative_ratio': negative_ratio,
                    'sentiment_balance': positive_ratio - negative_ratio,
                    'total_news': total
                }
        
        return {
            "time_patterns": time_patterns,
            "peak_hours": sorted(
                time_patterns.items(),
                key=lambda x: x[1]['total_news'],
                reverse=True
            )[:5]
        }

class TrendAnalyzer:
    """트렌드 분석기"""
    
    def __init__(self):
        self.trend_methods = {
            'linear': self._linear_trend_analysis,
            'moving_average': self._moving_average_analysis,
            'volatility': self._volatility_analysis
        }
    
    def analyze_sentiment_trend(self, sentiment_data: Dict) -> Dict[str, Any]:
        """감정 트렌드 분석"""
        if not sentiment_data:
            return {}
        
        try:
            dates = sorted(sentiment_data.keys())
            values = [sentiment_data[date] for date in dates]
            
            trends = {}
            for method_name, method_func in self.trend_methods.items():
                try:
                    trend_result = method_func(dates, values)
                    if trend_result:
                        trends[method_name] = trend_result
                except Exception as e:
                    logger.warning(f"트렌드 분석 실패 ({method_name}): {e}")
            
            return {
                "trends": trends,
                "data_points": len(values),
                "date_range": {
                    "start": min(dates) if dates else None,
                    "end": max(dates) if dates else None
                }
            }
        except Exception as e:
            logger.error(f"감정 트렌드 분석 실패: {e}")
            return {}
    
    def _linear_trend_analysis(self, dates, values) -> Dict[str, Any]:
        """선형 트렌드 분석"""
        if len(values) < 2:
            return None
        
        # 간단한 선형 회귀
        x = np.arange(len(values))
        y = np.array(values)
        
        slope = np.polyfit(x, y, 1)[0]
        
        return {
            "slope": slope,
            "direction": "upward" if slope > 0 else "downward" if slope < 0 else "stable",
            "strength": abs(slope)
        }
    
    def _moving_average_analysis(self, dates, values) -> Dict[str, Any]:
        """이동평균 분석"""
        if len(values) < 3:
            return None
        
        window = min(3, len(values))
        moving_avg = []
        
        for i in range(window - 1, len(values)):
            avg = sum(values[i-window+1:i+1]) / window
            moving_avg.append(avg)
        
        return {
            "moving_average": moving_avg,
            "trend": "increasing" if moving_avg[-1] > moving_avg[0] else "decreasing",
            "volatility": np.std(moving_avg)
        }
    
    def _volatility_analysis(self, dates, values) -> Dict[str, Any]:
        """변동성 분석"""
        if len(values) < 2:
            return None
        
        volatility = np.std(values)
        mean_value = np.mean(values)
        
        return {
            "volatility": volatility,
            "mean": mean_value,
            "coefficient_of_variation": volatility / abs(mean_value) if mean_value != 0 else 0
        }

# 전역 분석기 인스턴스
advanced_analyzer = AdvancedAnalyzer() 