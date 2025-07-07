import os
from dotenv import load_dotenv
from pymongo import MongoClient
from analyze_sentiment import analyze_sentiment
import pandas as pd

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI)
db = client["news_db"]
raw_col = db["raw_news"]
result_col = db["analyzed_news"]

# KRX 상장종목목록 CSV 다운로드 (코스피+코스닥)
url = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download"
df = pd.read_html(url, header=0)[0]
df = df[['회사명', '종목코드', '업종']]
df['종목코드'] = df['종목코드'].apply(lambda x: str(x).zfill(6))
stock_list = df.to_dict('records')

def extract_stocks_from_text(text, stock_list):
    found = []
    for stock in stock_list:
        if stock["회사명"] in text or (isinstance(stock["업종"], str) and stock["업종"] in text):
            found.append({
                "name": stock["회사명"],
                "code": stock["종목코드"],
                "sector": stock["업종"]
            })
    return found

def predict_direction(sentiment_label):
    if sentiment_label == 'positive':
        return '상승'
    elif sentiment_label == 'negative':
        return '하락'
    else:
        return '중립'

# 전체 뉴스 분석 및 종목/방향 예측
for news in raw_col.find().sort("published", -1):
    text = (news.get("content") or "") + " " + (news.get("title") or "")
    if not text.strip():
        continue
    sentiment = analyze_sentiment(text)
    related_stocks = extract_stocks_from_text(text, stock_list)
    for stock in related_stocks:
        stock["direction"] = predict_direction(sentiment['label'])
    analyzed = {
        "_id": news["_id"],
        "title": news.get("title"),
        "content": news.get("content"),
        "sentiment": sentiment,
        "published": news.get("published"),
        "link": news.get("link"),
        "related_stocks": related_stocks
    }
    result_col.replace_one({"_id": news["_id"]}, analyzed, upsert=True)
    print(f"분석 완료: {news.get('title')} → {sentiment}, 종목: {related_stocks}")
print("AI 감정분석+종목예측 파이프라인 완료") 