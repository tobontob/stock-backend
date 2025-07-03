import os
from dotenv import load_dotenv
from pymongo import MongoClient
from analyze_sentiment import analyze_sentiment

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI)
db = client["news_db"]
raw_col = db["raw_news"]
result_col = db["analyzed_news"]

# 최근 20개 뉴스만 예시로 분석
for news in raw_col.find().sort("published", -1).limit(20):
    text = news.get("content") or news.get("title")
    if not text:
        continue
    sentiment = analyze_sentiment(text)
    analyzed = {
        "_id": news["_id"],
        "title": news.get("title"),
        "content": news.get("content"),
        "sentiment": sentiment,  # label/score/probs 모두 저장
        "published": news.get("published"),
        "link": news.get("link")
    }
    result_col.replace_one({"_id": news["_id"]}, analyzed, upsert=True)
    print(f"분석 완료: {news.get('title')} → {sentiment}")
print("AI 감정분석 파이프라인 완료") 