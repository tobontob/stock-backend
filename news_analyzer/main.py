import os
from dotenv import load_dotenv
from pymongo import MongoClient
from analyze_sentiment import analyze_sentiment
import pandas as pd
import requests
from io import StringIO
import re

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI)
db = client["news_db"]
raw_col = db["raw_news"]
result_col = db["analyzed_news"]

print("=== 최신 코드 실행 중 ===")

# KRX 상장종목목록 CSV 다운로드 (코스피+코스닥)
print("KRX 종목 리스트 다운로드 중...")
url = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download"
response = requests.get(url)
response.encoding = 'euc-kr'
df = pd.read_html(StringIO(response.text), header=0)[0]
df = df[['회사명', '종목코드', '업종']]
df['종목코드'] = df['종목코드'].apply(lambda x: str(x).zfill(6))
stock_list = df.to_dict('records')

# 디버그 출력: 종목 리스트 로딩 확인
print(f"=== 종목 리스트 로딩 결과 ===")
print(f"총 {len(stock_list)}개 종목이 로딩되었습니다.")
print("\n=== 처음 5개 종목 예시 ===")
for i, stock in enumerate(stock_list[:5]):
    print(f"{i+1}. {stock['회사명']} ({stock['종목코드']}) - {stock['업종']}")

print("\n=== 마지막 5개 종목 예시 ===")
for i, stock in enumerate(stock_list[-5:]):
    print(f"{len(stock_list)-4+i}. {stock['회사명']} ({stock['종목코드']}) - {stock['업종']}")

print(f"\n=== 종목명 예시 (처음 10개) ===")
stock_names = [stock['회사명'] for stock in stock_list[:10]]
print(stock_names)

def extract_stocks_from_text(text, stock_list):
    found = []
    print(f"\n=== 종목 추출 디버그 ===")
    print(f"뉴스 텍스트 길이: {len(text)}")
    print(f"뉴스 텍스트 일부: {text[:200]}...")

    for stock in stock_list:
        stock_name = stock["회사명"]
        # 정규표현식: 종목명이 단어 경계(띄어쓰기, 문장부호, 문장 끝 등)로 구분되어 있는지 확인
        pattern = r'(\\b|\\s|^|[\\.,])' + re.escape(stock_name) + r'(\\b|\\s|$|[\\.,])'
        if re.search(pattern, text):
            found.append({
                "name": stock["회사명"],
                "code": stock["종목코드"],
                "sector": stock["업종"]
            })
            print(f"  ✓ 종목 발견: {stock['회사명']} ({stock['종목코드']})")

    # 중복 제거
    unique_found = []
    seen_names = set()
    for stock in found:
        if stock["name"] not in seen_names:
            unique_found.append(stock)
            seen_names.add(stock["name"])

    print(f"총 {len(unique_found)}개 종목이 추출되었습니다.")
    return unique_found

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