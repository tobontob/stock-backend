from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["news_db"]
result_col = db["analyzed_news"]

app = FastAPI()

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
    return {"message": "API is alive"}

@app.get("/analyzed_news")
def get_analyzed_news(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    try:
        skip = (page - 1) * page_size
        news_list = list(result_col.find().sort("published", -1).skip(skip).limit(page_size))
        total = result_col.count_documents({})
        for news in news_list:
            news["_id"] = str(news["_id"])
        return {"news": news_list, "total": total}
    except Exception as e:
        return {"error": str(e)} 