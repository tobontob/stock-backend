import os
from dotenv import load_dotenv
from pymongo import MongoClient
from analyze_sentiment import analyze_sentiment
from financial_keywords import financial_keyword_loader
import pandas as pd
import requests
from io import StringIO
import re
import time
from datetime import datetime, timedelta
import csv
import glob
from explain_util import generate_explanation
from article_crawler import fetch_article_content

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

# 종목 추출 관련 설정 추가
STOCK_EXTRACTION_CONFIG = {
    "max_title_length": 200,  # 제목에서 추출할 최대 길이
    "max_content_length": 500,  # 본문에서 추출할 최대 길이 (앞부분)
    "min_confidence": 0.6,  # 최소 신뢰도
    "blacklist": [
        "삼성전자", "LG전자", "현대차", "기아", "SK하이닉스",  # 너무 일반적인 종목들
        "카카오", "네이버", "쿠팡", "배달의민족",  # IT 대기업들
        "삼성생명", "교보생명", "한화생명",  # 보험사들
        "신한은행", "KB국민은행", "우리은행", "하나은행",  # 은행들
    ],
    "whitelist": {
        # 특정 업종에서 중요한 종목들
        "반도체": ["SK하이닉스", "삼성전자", "DB하이텍", "한미반도체"],
        "바이오": ["셀트리온", "삼성바이오로직스", "한미약품"],
        "자동차": ["현대차", "기아", "현대모비스", "LG화학"],
        "게임": ["넥슨", "넷마블", "크래프톤", "펄어비스"],
    }
}

def is_contextually_relevant(stock_name, text, position):
    """문맥적으로 관련성이 있는지 확인"""
    # 제목에 있으면 높은 우선순위
    if position == "title":
        return True
    
    # 본문 앞부분에 있으면 중간 우선순위
    if position == "content_front":
        return True
    
    # 본문 중간/뒤부분은 낮은 우선순위 (단, 특정 키워드와 함께 있으면 높은 우선순위)
    if position == "content_middle":
        # 금융 관련 키워드와 함께 있으면 우선순위 높임
        financial_keywords = ["주가", "주식", "투자", "매수", "매도", "상승", "하락", "실적", "매출", "이익"]
        for keyword in financial_keywords:
            if keyword in text and stock_name in text:
                return True
        return False
    
    return False

def extract_stocks_from_text(text, stock_list):
    found = []
    print(f"\n=== 종목 추출 디버그 ===")
    print(f"뉴스 텍스트 길이: {len(text)}")
    print(f"뉴스 텍스트 일부: {text[:200]}...")

    # 텍스트를 제목과 본문으로 분리 (간단한 추정)
    title_part = text[:STOCK_EXTRACTION_CONFIG["max_title_length"]]
    content_part = text[STOCK_EXTRACTION_CONFIG["max_title_length"]:STOCK_EXTRACTION_CONFIG["max_title_length"] + STOCK_EXTRACTION_CONFIG["max_content_length"]]
    
    for stock in stock_list:
        stock_name = stock["회사명"]
        
        # 블랙리스트 체크
        if stock_name in STOCK_EXTRACTION_CONFIG["blacklist"]:
            continue
        
        # 정규표현식: 종목명이 단어 경계로 구분되어 있는지 확인
        pattern = r'(\b|\s|^|[.,])' + re.escape(stock_name) + r'(\b|\s|$|[.,])'
        
        # 제목에서 검색
        if re.search(pattern, title_part):
            found.append({
                "name": stock["회사명"],
                "code": stock["종목코드"],
                "sector": stock["업종"],
                "position": "title",
                "confidence": 0.9
            })
            print(f"  ✓ 제목에서 종목 발견: {stock['회사명']} ({stock['종목코드']})")
            continue
        
        # 본문 앞부분에서 검색
        if re.search(pattern, content_part):
            found.append({
                "name": stock["회사명"],
                "code": stock["종목코드"],
                "sector": stock["업종"],
                "position": "content_front",
                "confidence": 0.7
            })
            print(f"  ✓ 본문 앞부분에서 종목 발견: {stock['회사명']} ({stock['종목코드']})")
            continue
        
        # 전체 텍스트에서 검색 (낮은 우선순위)
        if re.search(pattern, text):
            # 문맥적 관련성 확인
            if is_contextually_relevant(stock_name, text, "content_middle"):
                found.append({
                    "name": stock["회사명"],
                    "code": stock["종목코드"],
                    "sector": stock["업종"],
                    "position": "content_middle",
                    "confidence": 0.5
                })
                print(f"  ✓ 본문 중간에서 종목 발견: {stock['회사명']} ({stock['종목코드']})")
            else:
                found.append({
                    "name": stock["회사명"],
                    "code": stock["종목코드"],
                    "sector": stock["업종"],
                    "position": "content_other",
                    "confidence": 0.3
                })
                print(f"  ✓ 본문 기타에서 종목 발견: {stock['회사명']} ({stock['종목코드']})")

    # 신뢰도 기반 필터링 및 정렬
    filtered_found = [stock for stock in found if stock["confidence"] >= STOCK_EXTRACTION_CONFIG["min_confidence"]]
    filtered_found.sort(key=lambda x: x["confidence"], reverse=True)
    
    # 중복 제거 (높은 신뢰도 우선)
    unique_found = []
    seen_names = set()
    for stock in filtered_found:
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

# 1. 경제적 영향 룰셋 정의 (파일 상단에 추가)
IMPACT_RULES = financial_keyword_loader.get_impact_rules()

# 2. 키워드 추출 함수 (파일 상단에 추가)
def extract_impact_keywords(text, rules):
    found = []
    for keyword in rules.keys():
        if keyword in text:
            found.append(keyword)
    return found

# 3. 결합 분석 로직 (파일 상단에 추가)
def decide_final_label(sentiment, keywords, rules, title, content):
    impacts = [rules[k] for k in keywords]
    important_keywords = [k for k in keywords if k in title or k in content[:100]]
    if important_keywords:
        if "부정적" in [rules[k] for k in important_keywords]:
            return "부정적", f"핵심 키워드({', '.join(important_keywords)})가 기사 제목/첫문단에 등장하여 부정적 영향이 우선됩니다."
        elif "긍정적" in [rules[k] for k in important_keywords]:
            return "긍정적", f"핵심 키워드({', '.join(important_keywords)})가 기사 제목/첫문단에 등장하여 긍정적 영향이 우선됩니다."
    if sentiment['score'] and sentiment['score'] > 0.8:
        return sentiment['label'], f"감정분석 신뢰도가 높아 감정분석 결과({sentiment['label']})를 우선합니다."
    for k in keywords:
        if content.count(k) > 2:
            return rules[k], f"키워드({k})가 기사 내 여러 번 등장하여 해당 영향({rules[k]})을 우선합니다."
    return sentiment['label'], "특별한 우선순위 근거가 없어 감정분석 결과를 따릅니다."

# KNU 감성사전 txt 파일을 pandas로 불러와 긍/부정 단어 세트로 만드는 코드 (자동 경로 탐색)
def load_knu_sentilex():
    # 여러 경로에서 SentiWord_Dict.txt 파일 자동 탐색
    search_paths = [
        'SentiWord_Dict.txt',  # 현재 디렉토리
        '../SentiWord_Dict.txt',  # 상위 디렉토리
        '../../SentiWord_Dict.txt',  # 상위 상위 디렉토리
        'KnuSentiLex*/**/SentiWord_Dict.txt',  # KnuSentiLex 폴더 내
        '**/SentiWord_Dict.txt'  # 모든 하위 폴더
    ]
    
    candidates = []
    for pattern in search_paths:
        if '*' in pattern:
            candidates.extend(glob.glob(pattern, recursive=True))
        else:
            if os.path.exists(pattern):
                candidates.append(pattern)
    
    if not candidates:
        print('[감성사전 경고] SentiWord_Dict.txt 파일을 찾을 수 없습니다.')
        return set(), set()
    
    path = candidates[0]
    print(f'[감성사전] 파일 발견: {path}')
    
    try:
        # 헤더가 없는 형식이므로 컬럼명을 직접 지정
        df = pd.read_csv(path, sep='\t', encoding='utf-8', header=None, names=['word', 'polarity'])
        pos_words = set(df[df['polarity'] > 0]['word'])
        neg_words = set(df[df['polarity'] < 0]['word'])
        print(f'[감성사전] 긍정 {len(pos_words)}개, 부정 {len(neg_words)}개 단어 로딩 완료')
        return pos_words, neg_words
    except Exception as e:
        print(f'[감성사전 로딩 오류] {e}')
        return set(), set()

positive_words, negative_words = load_knu_sentilex()

# 감성사전 기반 감정 점수 계산 함수 (파일 상단에 추가)
def count_sentiment_words(text, pos_words, neg_words):
    words = re.findall(r'[가-힣]{2,}', text)
    pos = sum(1 for w in words if w in pos_words)
    neg = sum(1 for w in words if w in neg_words)
    score = pos - neg
    return {'positive': pos, 'negative': neg, 'score': score}

def process_news_batch(news_list, stock_list):
    """뉴스 배치를 처리하는 함수"""
    processed_count = 0
    for news in news_list:
        try:
            title = news.get("title") or ""
            content = news.get("content") or ""
            # 본문이 없거나 너무 짧으면 링크에서 실시간 크롤링 시도
            if not content or len(content.strip()) < 50:
                link = news.get("link")
                if link:
                    crawled_content = fetch_article_content(link)
                    if crawled_content and len(crawled_content.strip()) > 50:
                        content = crawled_content
            if content and len(content.strip()) > 50:
                text = content + " " + title
            else:
                text = title
            if not text.strip():
                continue
            sentiment = analyze_sentiment(text)
            # --- 감성사전 기반 감정 점수 분석 ---
            senti_score = count_sentiment_words(text, positive_words, negative_words)
            
            # --- 금융 키워드 분석 ---
            financial_keywords = financial_keyword_loader.extract_financial_keywords_from_text(text)
            sentiment_keywords = financial_keyword_loader.extract_sentiment_keywords_from_text(text)
            impact_score = financial_keyword_loader.get_impact_score(text)
            
            related_stocks = extract_stocks_from_text(text, stock_list)
            
            # === 설명형 분석근거 생성 (개선된 버전) ===
            if related_stocks:
                main_stock = related_stocks[0]
                company_name = main_stock["name"]
                industry = main_stock["sector"] if main_stock.get("sector") else "전 업종"
            else:
                company_name = "해당없음"
                industry = "전 업종"
            
            # 감정에 따른 설명 생성
            sentiment_label = sentiment['label']
            explanation = generate_explanation(text, company_name, industry)
            
            # 다중 관점 설명 생성 (새로운 기능)
            from explain_util import generate_multi_perspective_explanation, enhance_explanation_with_data
            
            multi_explanations = generate_multi_perspective_explanation(
                text, company_name, industry, sentiment_label
            )
            
            # 추가 데이터로 설명 강화
            additional_data = {
                'sentiment_score': sentiment.get('score', 0),
                'keyword_count': len(financial_keywords.get('stock_keywords', [])) + len(sentiment_keywords.get('positive', [])) + len(sentiment_keywords.get('negative', []))
            }
            
            enhanced_explanation = enhance_explanation_with_data(explanation, additional_data)
            
            # 종목별 방향 예측 개선
            for stock in related_stocks:
                # 신뢰도 기반 방향 예측
                confidence = stock.get("confidence", 0.5)
                if confidence > 0.8:
                    stock["direction"] = predict_direction(sentiment['label'])
                    stock["confidence_level"] = "높음"
                elif confidence > 0.6:
                    stock["direction"] = predict_direction(sentiment['label'])
                    stock["confidence_level"] = "보통"
                else:
                    stock["direction"] = "중립"
                    stock["confidence_level"] = "낮음"
                
                # 종목별 상세 정보 추가
                stock["analysis_details"] = {
                    "position": stock.get("position", "unknown"),
                    "sentiment_score": sentiment.get('score', 0),
                    "financial_keywords": len(financial_keywords.get('stock_keywords', [])),
                    "sentiment_keywords": len(sentiment_keywords.get('positive', [])) + len(sentiment_keywords.get('negative', []))
                }
            
            # --- 키워드 추출 및 결합분석 ---
            keywords = extract_impact_keywords(text, IMPACT_RULES)
            final_label, reason_detail = decide_final_label(sentiment, keywords, IMPACT_RULES, title, content)
            
            # 금융 키워드 정보 추가
            financial_keyword_info = []
            for category, keywords_list in financial_keywords.items():
                if keywords_list:
                    financial_keyword_info.append(f"{category}: {', '.join(keywords_list)}")
            
            sentiment_keyword_info = []
            for sentiment_type, keywords_list in sentiment_keywords.items():
                if keywords_list:
                    sentiment_keyword_info.append(f"{sentiment_type}: {', '.join(keywords_list)}")
            
            reason = ""
            if enhanced_explanation:
                reason += f"[설명형 분석근거] {enhanced_explanation}\n"
            reason += f"[결합분석] {reason_detail} (감정분석: {sentiment['reason']}, 키워드: {', '.join(keywords) if keywords else '없음'}, 감성사전 점수: {senti_score}, 금융키워드: {'; '.join(financial_keyword_info) if financial_keyword_info else '없음'}, 감정키워드: {'; '.join(sentiment_keyword_info) if sentiment_keyword_info else '없음'}, 영향도점수: {impact_score})"
            
            # 다중 관점 설명 추가
            if multi_explanations:
                reason += f"\n[다중관점분석] 시장관점: {multi_explanations.get('market', 'N/A')}, 업종관점: {multi_explanations.get('sector', 'N/A')}, 트렌드관점: {multi_explanations.get('trend', 'N/A')}"
            
            analyzed = {
                "_id": news["_id"],
                "title": news.get("title"),
                "content": news.get("content"),
                "sentiment": sentiment,
                "senti_score": senti_score,  # 감성사전 점수 추가
                "financial_keywords": financial_keywords,  # 금융 키워드 추가
                "sentiment_keywords": sentiment_keywords,  # 감정 키워드 추가
                "impact_score": impact_score,  # 영향도 점수 추가
                "published": news.get("published"),
                "link": news.get("link"),
                "related_stocks": related_stocks,
                "reason": reason,  # 결합분석 근거
                "final_label": final_label,  # 결합분석 최종 방향
                "multi_perspective_analysis": multi_explanations,  # 다중 관점 분석
                "analysis_quality": {
                    "sentiment_confidence": sentiment.get('score', 0),
                    "keyword_diversity": len(financial_keywords.get('stock_keywords', [])),
                    "stock_extraction_confidence": related_stocks[0].get("confidence", 0) if related_stocks else 0,
                    "explanation_quality": len(enhanced_explanation) if enhanced_explanation else 0
                }
            }
            result_col.replace_one({"_id": news["_id"]}, analyzed, upsert=True)
            print(f"분석 완료: {news.get('title')} → {sentiment}, 감성사전: {senti_score}, 종목: {related_stocks}, 결합분석: {final_label}, 근거: {reason}")
            processed_count += 1
        except Exception as e:
            print(f"뉴스 처리 중 오류 발생: {news.get('title', 'Unknown')} - {e}")
            continue
    return processed_count

# 전체 뉴스 분석 및 종목/방향 예측 (배치 처리)
print("뉴스 분석 시작...")

# 최근 7일 이내 뉴스만 분석 (날짜 필터링 확장)
recent_time = datetime.utcnow() - timedelta(days=7)
print(f"분석 대상 기간: 최근 7일 ({recent_time} ~ 현재)")

# 강제 재분석 옵션 (환경변수로 제어)
FORCE_REANALYZE = os.getenv("FORCE_REANALYZE", "false").lower() == "true"

if FORCE_REANALYZE:
    print("⚠️ 강제 재분석 모드 활성화 - 모든 뉴스를 재분석합니다.")
    target_news_cursor = raw_col.find({
        "published": {"$gte": recent_time}
    }).sort("published", -1).limit(100)
    target_news_list = list(target_news_cursor)
    print(f"재분석 대상 뉴스: {len(target_news_list)}개")
else:
    # 이미 분석된 뉴스 ID 목록 가져오기
    print("이미 분석된 뉴스 확인 중...")
    already_analyzed_ids = set(doc["_id"] for doc in result_col.find({}, {"_id": 1}))
    print(f"이미 분석된 뉴스: {len(already_analyzed_ids)}개")

    # 분석 대상 뉴스만 추출 (이미 분석된 것 제외, 최근 7일 이내)
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