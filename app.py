from fastapi import FastAPI
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
def get_analyzed_news():
    try:
        news_list = list(result_col.find().sort("published", -1).limit(20))
        for news in news_list:
            news["_id"] = str(news["_id"])
        return {"news": news_list}
    except Exception as e:
        return {"error": str(e)} 