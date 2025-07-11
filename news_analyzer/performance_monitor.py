#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
성능 모니터링 및 분석 품질 지표 추적
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class AnalysisMetrics:
    """분석 품질 지표"""
    sentiment_confidence: float
    keyword_diversity: int
    stock_extraction_confidence: float
    explanation_quality: int
    processing_time: float
    text_length: int
    stock_count: int
    keyword_count: int

@dataclass
class PerformanceMetrics:
    """성능 지표"""
    total_processed: int
    total_failed: int
    avg_processing_time: float
    success_rate: float
    start_time: datetime
    end_time: datetime

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.metrics_history: List[AnalysisMetrics] = []
        self.performance_history: List[PerformanceMetrics] = []
        self.current_batch_start = None
        self.current_batch_metrics = []
    
    def start_batch_monitoring(self):
        """배치 처리 모니터링 시작"""
        self.current_batch_start = time.time()
        self.current_batch_metrics = []
        logger.info("배치 처리 모니터링 시작")
    
    def record_analysis_metrics(self, metrics: AnalysisMetrics):
        """개별 분석 품질 지표 기록"""
        self.current_batch_metrics.append(metrics)
        self.metrics_history.append(metrics)
        
        # 실시간 품질 체크
        self._check_quality_thresholds(metrics)
    
    def _check_quality_thresholds(self, metrics: AnalysisMetrics):
        """품질 임계값 체크"""
        warnings = []
        
        if metrics.sentiment_confidence < 0.5:
            warnings.append(f"낮은 감정분석 신뢰도: {metrics.sentiment_confidence}")
        
        if metrics.stock_extraction_confidence < 0.6:
            warnings.append(f"낮은 종목추출 신뢰도: {metrics.stock_extraction_confidence}")
        
        if metrics.keyword_diversity < 3:
            warnings.append(f"낮은 키워드 다양성: {metrics.keyword_diversity}")
        
        if metrics.processing_time > 10.0:
            warnings.append(f"긴 처리 시간: {metrics.processing_time:.2f}초")
        
        if warnings:
            logger.warning(f"품질 경고: {'; '.join(warnings)}")
    
    def end_batch_monitoring(self, total_processed: int, total_failed: int):
        """배치 처리 모니터링 종료"""
        if not self.current_batch_start:
            return
        
        end_time = time.time()
        processing_time = end_time - self.current_batch_start
        
        # 성능 지표 계산
        success_rate = total_processed / (total_processed + total_failed) if (total_processed + total_failed) > 0 else 0
        avg_processing_time = sum(m.processing_time for m in self.current_batch_metrics) / len(self.current_batch_metrics) if self.current_batch_metrics else 0
        
        performance_metrics = PerformanceMetrics(
            total_processed=total_processed,
            total_failed=total_failed,
            avg_processing_time=avg_processing_time,
            success_rate=success_rate,
            start_time=datetime.fromtimestamp(self.current_batch_start),
            end_time=datetime.fromtimestamp(end_time)
        )
        
        self.performance_history.append(performance_metrics)
        
        # 성능 리포트 출력
        self._print_performance_report(performance_metrics)
        
        logger.info(f"배치 처리 완료: 성공 {total_processed}개, 실패 {total_failed}개, 평균 처리시간 {avg_processing_time:.2f}초")
    
    def _print_performance_report(self, metrics: PerformanceMetrics):
        """성능 리포트 출력"""
        print("\n" + "="*60)
        print("📊 성능 리포트")
        print("="*60)
        print(f"처리된 뉴스: {metrics.total_processed}개")
        print(f"실패한 뉴스: {metrics.total_failed}개")
        print(f"성공률: {metrics.success_rate:.1%}")
        print(f"평균 처리시간: {metrics.avg_processing_time:.2f}초")
        print(f"총 소요시간: {(metrics.end_time - metrics.start_time).total_seconds():.2f}초")
        print("="*60)
    
    def get_quality_summary(self, days: int = 7) -> Dict[str, Any]:
        """품질 요약 통계"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_metrics = [m for m in self.metrics_history if hasattr(m, 'timestamp') and m.timestamp > cutoff_date]
        
        if not recent_metrics:
            return {}
        
        return {
            "avg_sentiment_confidence": sum(m.sentiment_confidence for m in recent_metrics) / len(recent_metrics),
            "avg_stock_confidence": sum(m.stock_extraction_confidence for m in recent_metrics) / len(recent_metrics),
            "avg_keyword_diversity": sum(m.keyword_diversity for m in recent_metrics) / len(recent_metrics),
            "avg_processing_time": sum(m.processing_time for m in recent_metrics) / len(recent_metrics),
            "total_analyses": len(recent_metrics)
        }
    
    def export_metrics(self, filename: str = None):
        """지표 내보내기"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_metrics_{timestamp}.json"
        
        export_data = {
            "metrics_history": [asdict(m) for m in self.metrics_history],
            "performance_history": [asdict(m) for m in self.performance_history],
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"지표가 {filename}에 저장되었습니다.")
        return filename

class QualityAnalyzer:
    """분석 품질 분석기"""
    
    def __init__(self):
        self.quality_thresholds = {
            "sentiment_confidence": 0.6,
            "stock_confidence": 0.7,
            "keyword_diversity": 3,
            "processing_time": 5.0
        }
    
    def analyze_quality(self, metrics: AnalysisMetrics) -> Dict[str, Any]:
        """개별 분석 품질 평가"""
        quality_score = 0
        issues = []
        
        # 감정분석 신뢰도 평가
        if metrics.sentiment_confidence >= self.quality_thresholds["sentiment_confidence"]:
            quality_score += 25
        else:
            issues.append("낮은 감정분석 신뢰도")
        
        # 종목추출 신뢰도 평가
        if metrics.stock_extraction_confidence >= self.quality_thresholds["stock_confidence"]:
            quality_score += 25
        else:
            issues.append("낮은 종목추출 신뢰도")
        
        # 키워드 다양성 평가
        if metrics.keyword_diversity >= self.quality_thresholds["keyword_diversity"]:
            quality_score += 25
        else:
            issues.append("낮은 키워드 다양성")
        
        # 처리시간 평가
        if metrics.processing_time <= self.quality_thresholds["processing_time"]:
            quality_score += 25
        else:
            issues.append("긴 처리시간")
        
        return {
            "quality_score": quality_score,
            "grade": self._get_quality_grade(quality_score),
            "issues": issues,
            "recommendations": self._get_recommendations(issues)
        }
    
    def _get_quality_grade(self, score: int) -> str:
        """품질 등급 반환"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C"
        else:
            return "D"
    
    def _get_recommendations(self, issues: List[str]) -> List[str]:
        """개선 권장사항"""
        recommendations = []
        
        if "낮은 감정분석 신뢰도" in issues:
            recommendations.append("감정분석 모델의 정확도 향상이 필요합니다")
        
        if "낮은 종목추출 신뢰도" in issues:
            recommendations.append("종목추출 알고리즘의 정확도 개선이 필요합니다")
        
        if "낮은 키워드 다양성" in issues:
            recommendations.append("키워드 추출 알고리즘의 다양성 확보가 필요합니다")
        
        if "긴 처리시간" in issues:
            recommendations.append("처리 성능 최적화가 필요합니다")
        
        return recommendations

# 전역 모니터 인스턴스
performance_monitor = PerformanceMonitor()
quality_analyzer = QualityAnalyzer()

def monitor_analysis_performance(func):
    """분석 성능 모니터링 데코레이터"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # 성능 지표 수집
            processing_time = time.time() - start_time
            
            # 텍스트 길이 추정 (첫 번째 인자가 텍스트라고 가정)
            text_length = len(args[0]) if args else 0
            
            # 결과에서 지표 추출
            sentiment_confidence = result.get('sentiment', {}).get('score', 0) if isinstance(result, dict) else 0
            stock_count = len(result.get('related_stocks', [])) if isinstance(result, dict) else 0
            keyword_count = len(result.get('financial_keywords', {}).get('stock_keywords', [])) if isinstance(result, dict) else 0
            
            metrics = AnalysisMetrics(
                sentiment_confidence=sentiment_confidence,
                keyword_diversity=keyword_count,
                stock_extraction_confidence=0.7,  # 기본값
                explanation_quality=len(result.get('reason', '')) if isinstance(result, dict) else 0,
                processing_time=processing_time,
                text_length=text_length,
                stock_count=stock_count,
                keyword_count=keyword_count
            )
            
            performance_monitor.record_analysis_metrics(metrics)
            
            return result
            
        except Exception as e:
            logger.error(f"분석 중 오류 발생: {e}")
            raise
    
    return wrapper 