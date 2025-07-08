import os
from dotenv import load_dotenv
from pymongo import MongoClient
from analyze_sentiment import analyze_sentiment
import pandas as pd
import requests
from io import StringIO
import re
import time
from datetime import datetime, timedelta

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=30000, socketTimeoutMS=30000)
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
        pattern = r'(\b|\s|^|[.,])' + re.escape(stock_name) + r'(\b|\s|$|[.,])'
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

def process_news_batch(news_list, stock_list):
    """뉴스 배치를 처리하는 함수"""
    processed_count = 0
    for news in news_list:
        try:
            title = news.get("title") or ""
            content = news.get("content") or ""
            
            # 본문이 있으면 본문을 우선 분석, 없으면 제목만 분석
            if content and len(content.strip()) > 50:  # 본문이 50자 이상이면
                text = content + " " + title  # 본문 + 제목
                print(f"본문 분석: {len(content)}자 본문 + 제목")
            else:
                text = title  # 제목만
                print(f"제목만 분석: {len(title)}자 제목")
            
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
            processed_count += 1
            
        except Exception as e:
            print(f"뉴스 처리 중 오류 발생: {news.get('title', 'Unknown')} - {e}")
            continue
    
    return processed_count

# 전체 뉴스 분석 및 종목/방향 예측 (배치 처리)
print("뉴스 분석 시작...")

# 최근 2일 이내 뉴스만 분석 (날짜 필터링)
recent_time = datetime.utcnow() - timedelta(days=2)
print(f"분석 대상 기간: 최근 2일 ({recent_time} ~ 현재)")

# 이미 분석된 뉴스 ID 목록 가져오기
print("이미 분석된 뉴스 확인 중...")
already_analyzed_ids = set(doc["_id"] for doc in result_col.find({}, {"_id": 1}))
print(f"이미 분석된 뉴스: {len(already_analyzed_ids)}개")

# 분석 대상 뉴스만 추출 (이미 분석된 것 제외, 최근 2일 이내)
target_news_cursor = raw_col.find({
    "_id": {"$nin": list(already_analyzed_ids)},
    "published": {"$gte": recent_time}
}).sort("published", -1).limit(100)
target_news_list = list(target_news_cursor)

print(f"분석 대상 뉴스: {len(target_news_list)}개")

if len(target_news_list) == 0:
    print("분석할 새로운 뉴스가 없습니다.")
    exit()

max_retries = 3
batch_size = 10  # 한 번에 처리할 뉴스 수

for attempt in range(max_retries):
    try:
        # 배치 단위로 뉴스를 처리
        news_batch = []
        
        for news in target_news_list:
            news_batch.append(news)
            if len(news_batch) >= batch_size:
                print(f"배치 처리 중... ({len(news_batch)}개)")
                processed = process_news_batch(news_batch, stock_list)
                print(f"배치 완료: {processed}개 처리됨")
                news_batch = []
                time.sleep(1)  # 1초 대기
        
        # 남은 뉴스 처리
        if news_batch:
            print(f"마지막 배치 처리 중... ({len(news_batch)}개)")
            processed = process_news_batch(news_batch, stock_list)
            print(f"마지막 배치 완료: {processed}개 처리됨")
        
        print("AI 감정분석+종목예측 파이프라인 완료")
        break
        
    except Exception as e:
        print(f"시도 {attempt + 1}/{max_retries} 실패: {e}")
        if attempt < max_retries - 1:
            print("5초 후 재시도...")
            time.sleep(5)
        else:
            print("최대 재시도 횟수 초과. 분석을 중단합니다.")
            raise e 