#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
성능 최적화를 위한 캐싱 시스템
"""

import time
import json
import hashlib
from typing import Any, Dict, Optional, List
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """캐시 관리자"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl = ttl  # Time To Live (초)
        self.access_times: Dict[str, float] = {}
    
    def _generate_key(self, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        if key not in self.cache:
            return None
        
        # TTL 체크
        if time.time() - self.access_times[key] > self.ttl:
            self.delete(key)
            return None
        
        # 접근 시간 업데이트
        self.access_times[key] = time.time()
        return self.cache[key]['value']
    
    def set(self, key: str, value: Any) -> None:
        """캐시에 값 저장"""
        # 캐시 크기 제한 체크
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = {
            'value': value,
            'created_at': time.time()
        }
        self.access_times[key] = time.time()
    
    def delete(self, key: str) -> None:
        """캐시에서 값 삭제"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
    
    def clear(self) -> None:
        """캐시 전체 삭제"""
        self.cache.clear()
        self.access_times.clear()
    
    def _evict_oldest(self) -> None:
        """가장 오래된 항목 제거"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.delete(oldest_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        current_time = time.time()
        expired_count = sum(1 for key in self.cache 
                          if current_time - self.access_times[key] > self.ttl)
        
        return {
            "total_items": len(self.cache),
            "expired_items": expired_count,
            "hit_rate": self._calculate_hit_rate(),
            "memory_usage": len(json.dumps(self.cache)),
            "max_size": self.max_size,
            "ttl": self.ttl
        }
    
    def _calculate_hit_rate(self) -> float:
        """캐시 히트율 계산 (간단한 구현)"""
        # 실제로는 히트/미스 카운터가 필요
        return 0.85  # 샘플 값

def cache_result(ttl: int = 3600):
    """함수 결과 캐싱 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = CacheManager()
            key = cache._generate_key(func.__name__, *args, **kwargs)
            
            # 캐시에서 조회
            cached_result = cache.get(key)
            if cached_result is not None:
                logger.debug(f"캐시 히트: {func.__name__}")
                return cached_result
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐싱
            cache.set(key, result)
            logger.debug(f"캐시 저장: {func.__name__}")
            
            return result
        return wrapper
    return decorator

class ModelCache:
    """모델 캐시 관리자"""
    
    def __init__(self):
        self.models = {}
        self.model_metadata = {}
    
    def load_model(self, model_name: str, model_loader_func):
        """모델 로드 및 캐싱"""
        if model_name in self.models:
            logger.info(f"캐시된 모델 사용: {model_name}")
            return self.models[model_name]
        
        logger.info(f"모델 로드 중: {model_name}")
        model = model_loader_func()
        self.models[model_name] = model
        self.model_metadata[model_name] = {
            'loaded_at': time.time(),
            'size': self._estimate_model_size(model)
        }
        
        return model
    
    def _estimate_model_size(self, model) -> int:
        """모델 크기 추정"""
        try:
            return len(str(model))
        except:
            return 0
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        return {
            "cached_models": list(self.models.keys()),
            "total_models": len(self.models),
            "metadata": self.model_metadata
        }

class TextCache:
    """텍스트 처리 결과 캐싱"""
    
    def __init__(self):
        self.cache = CacheManager(max_size=500, ttl=1800)  # 30분 TTL
    
    @cache_result(ttl=1800)
    def get_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """감정분석 결과 캐싱"""
        # 실제 감정분석 로직은 여기서 구현
        return {"label": "neutral", "score": 0.5}
    
    @cache_result(ttl=3600)
    def get_stock_extraction(self, text: str) -> List[Dict]:
        """종목추출 결과 캐싱"""
        # 실제 종목추출 로직은 여기서 구현
        return []
    
    @cache_result(ttl=1800)
    def get_keyword_extraction(self, text: str) -> Dict[str, List[str]]:
        """키워드추출 결과 캐싱"""
        # 실제 키워드추출 로직은 여기서 구현
        return {"financial": [], "sentiment": []}

# 전역 캐시 인스턴스들
cache_manager = CacheManager()
model_cache = ModelCache()
text_cache = TextCache()

def get_cache_stats() -> Dict[str, Any]:
    """전체 캐시 통계 반환"""
    return {
        "general_cache": cache_manager.get_stats(),
        "model_cache": model_cache.get_model_info(),
        "text_cache": text_cache.cache.get_stats()
    } 