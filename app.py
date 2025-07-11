from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from typing import List, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["news_db"]
result_col = db["analyzed_news"]

app = FastAPI(title="뉴스 분석 API", description="AI 기반 뉴스 감정분석 및 종목예측 API")

# CORS 허용 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포시에는 프론트엔드 도메인만 허용 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "뉴스 분석 API가 정상적으로 동작 중입니다"}

@app.get("/analyzed_news")
def get_analyzed_news(
    limit: Optional[int] = Query(100, description="조회할 뉴스 개수"),
    sentiment: Optional[str] = Query(None, description="감정 필터 (positive/negative/neutral)"),
    company: Optional[str] = Query(None, description="특정 회사명으로 필터링"),
    sector: Optional[str] = Query(None, description="특정 업종으로 필터링")
):
    """분석된 뉴스 목록 조회"""
    try:
        # 필터 조건 구성
        filter_conditions = {}
        
        if sentiment:
            filter_conditions["sentiment.label"] = sentiment
        
        if company:
            filter_conditions["related_stocks.name"] = {"$regex": company, "$options": "i"}
        
        if sector:
            filter_conditions["related_stocks.sector"] = {"$regex": sector, "$options": "i"}
        
        # 뉴스 조회
        news_list = list(result_col.find(filter_conditions).sort("published", -1).limit(limit))
        
        # ObjectId를 문자열로 변환
        for news in news_list:
            news["_id"] = str(news["_id"])
        
        return {
            "success": True,
            "count": len(news_list),
            "news": news_list
        }
    except Exception as e:
        logger.error(f"뉴스 조회 중 오류: {e}")
        return {"success": False, "error": str(e)}

@app.get("/news/{news_id}")
def get_news_detail(news_id: str):
    """특정 뉴스 상세 정보 조회"""
    try:
        from bson import ObjectId
        news = result_col.find_one({"_id": ObjectId(news_id)})
        
        if not news:
            return {"success": False, "error": "뉴스를 찾을 수 없습니다"}
        
        news["_id"] = str(news["_id"])
        return {"success": True, "news": news}
    except Exception as e:
        logger.error(f"뉴스 상세 조회 중 오류: {e}")
        return {"success": False, "error": str(e)}

@app.get("/analysis/quality")
def get_analysis_quality():
    """분석 품질 통계 조회"""
    try:
        # 전체 분석된 뉴스 수
        total_count = result_col.count_documents({})
        
        # 감정별 분포
        sentiment_stats = list(result_col.aggregate([
            {"$group": {"_id": "$sentiment.label", "count": {"$sum": 1}}}
        ]))
        
        # 신뢰도 통계
        confidence_stats = list(result_col.aggregate([
            {"$group": {
                "_id": None,
                "avg_sentiment_confidence": {"$avg": "$analysis_quality.sentiment_confidence"},
                "avg_keyword_diversity": {"$avg": "$analysis_quality.keyword_diversity"},
                "avg_stock_confidence": {"$avg": "$analysis_quality.stock_extraction_confidence"}
            }}
        ]))
        
        # 최근 분석된 뉴스 (최근 24시간)
        from datetime import datetime, timedelta
        recent_time = datetime.utcnow() - timedelta(hours=24)
        recent_count = result_col.count_documents({"published": {"$gte": recent_time}})
        
        return {
            "success": True,
            "total_analyzed": total_count,
            "recent_analyzed": recent_count,
            "sentiment_distribution": sentiment_stats,
            "quality_metrics": confidence_stats[0] if confidence_stats else {}
        }
    except Exception as e:
        logger.error(f"분석 품질 통계 조회 중 오류: {e}")
        return {"success": False, "error": str(e)}

@app.get("/stocks/popular")
def get_popular_stocks(limit: Optional[int] = Query(10, description="조회할 종목 개수")):
    """자주 언급되는 종목 조회"""
    try:
        # 종목별 언급 횟수 집계
        stock_stats = list(result_col.aggregate([
            {"$unwind": "$related_stocks"},
            {"$group": {
                "_id": "$related_stocks.name",
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$related_stocks.confidence"},
                "sector": {"$first": "$related_stocks.sector"},
                "code": {"$first": "$related_stocks.code"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]))
        
        return {
            "success": True,
            "stocks": stock_stats
        }
    except Exception as e:
        logger.error(f"인기 종목 조회 중 오류: {e}")
        return {"success": False, "error": str(e)}

@app.get("/sentiment/trend")
def get_sentiment_trend(days: Optional[int] = Query(7, description="조회할 일수")):
    """감정 트렌드 조회"""
    try:
        from datetime import datetime, timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 일별 감정 분포
        daily_sentiment = list(result_col.aggregate([
            {"$match": {"published": {"$gte": start_date}}},
            {"$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$published"}},
                    "sentiment": "$sentiment.label"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.date": 1}}
        ]))
        
        return {
            "success": True,
            "trend": daily_sentiment
        }
    except Exception as e:
        logger.error(f"감정 트렌드 조회 중 오류: {e}")
        return {"success": False, "error": str(e)}

@app.get("/health")
def health_check():
    """헬스 체크"""
    try:
        # MongoDB 연결 확인
        db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 