#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모두의말뭉치 신문 데이터에서 경제/금융 키워드 추출 및 경량화
"""

import pandas as pd
import re
import json
from collections import Counter
import glob
import os
from typing import Dict, List, Set, Tuple

# 경제/금융 관련 키워드 패턴
ECONOMIC_PATTERNS = {
    # 주식/투자 관련
    'stock_keywords': [
        '주식', '주가', '상장', '상장폐지', 'IPO', '공모주', '배당', '주주', '시가총액',
        'PER', 'PBR', 'ROE', 'EPS', 'BPS', '배당률', '배당수익률', '자기주식',
        '스톡옵션', '스톡옵션', '우선주', '보통주', '전환사채', '신주인수권증권'
    ],
    
    # 경제 지표
    'economic_indicators': [
        'GDP', 'GNP', '인플레이션', '물가상승률', 'CPI', 'PPI', '실업률', '고용률',
        '금리', '기준금리', 'LIBOR', 'CD금리', '국채금리', '회사채금리',
        '환율', '달러환율', '엔환율', '유로환율', '원화강세', '원화약세',
        '무역수지', '경상수지', '자본수지', '외환보유액', '외채'
    ],
    
    # 기업 활동
    'corporate_activities': [
        '실적', '매출', '영업이익', '당기순이익', '영업손실', '적자', '흑자',
        '매출액', '영업이익률', '순이익률', '부채비율', '유동비율', '당좌비율',
        '투자', 'M&A', '합병', '분할', '스핀오프', '자회사', '지주회사',
        '신제품', 'R&D', '연구개발', '특허', '라이센스', '기술이전'
    ],
    
    # 금융/은행
    'financial_keywords': [
        '은행', '대출', '대출금리', '담보', '부동산담보', '신용대출', '카드론',
        '예금', '적금', '정기예금', '정기적금', '금융상품', '펀드', 'ETF',
        '보험', '생명보험', '손해보험', '연금', '연금보험', '퇴직연금',
        '증권', '증권사', '투자신탁', '사모펀드', '벤처캐피탈'
    ],
    
    # 정책/규제
    'policy_keywords': [
        '금융정책', '통화정책', '재정정책', '규제', '규제완화', '규제강화',
        '세금', '법인세', '소득세', '부가가치세', '양도소득세', '증여세',
        '정부지원', '보조금', '세제혜택', '감세', '증세', '조세정책'
    ],
    
    # 산업별
    'industry_keywords': [
        '반도체', '자동차', '조선', '철강', '화학', '제약', '바이오',
        'IT', '소프트웨어', '하드웨어', '인터넷', '모바일', 'AI', '블록체인',
        '에너지', '석유', '가스', '전기', '신재생에너지', '태양광', '풍력',
        '건설', '부동산', '아파트', '오피스텔', '상가', '토지'
    ]
}

# 감정 분류 키워드
SENTIMENT_KEYWORDS = {
    'positive': [
        '상승', '급등', '호조', '성장', '확대', '증가', '개선', '회복',
        '돌파', '신고점', '최고점', '기대', '긍정', '낙관', '강세',
        '투자유치', '성과', '실적호조', '매출증가', '이익증가', '배당증가'
    ],
    'negative': [
        '하락', '급락', '악화', '감소', '축소', '위축', '부정', '비관',
        '하향', '최저점', '신저점', '우려', '리스크', '위험', '약세',
        '실적악화', '손실', '적자', '부도', '파산', '청산', '폐업'
    ],
    'neutral': [
        '유지', '보합', '안정', '중립', '관망', '대기', '검토', '검토중',
        '변화없음', '동결', '동일', '유사', '비슷', '일정'
    ]
}

def load_mudeung_corpus(file_path: str) -> List[str]:
    """모두의말뭉치 파일 로드"""
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [item.get('text', '') for item in data]
        else:
            print(f"지원하지 않는 파일 형식: {file_path}")
            return []
    except Exception as e:
        print(f"파일 로드 오류: {e}")
        return []

def extract_financial_keywords(text: str) -> Dict[str, List[str]]:
    """텍스트에서 경제/금융 키워드 추출"""
    found_keywords = {category: [] for category in ECONOMIC_PATTERNS.keys()}
    
    for category, keywords in ECONOMIC_PATTERNS.items():
        for keyword in keywords:
            if keyword in text:
                found_keywords[category].append(keyword)
    
    return found_keywords

def extract_sentiment_keywords(text: str) -> Dict[str, List[str]]:
    """텍스트에서 감정 키워드 추출"""
    found_sentiments = {sentiment: [] for sentiment in SENTIMENT_KEYWORDS.keys()}
    
    for sentiment, keywords in SENTIMENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                found_sentiments[sentiment].append(keyword)
    
    return found_sentiments

def create_financial_keyword_dataset(corpus_files: List[str]) -> Dict:
    """경제/금융 키워드 데이터셋 생성"""
    all_financial_keywords = {category: Counter() for category in ECONOMIC_PATTERNS.keys()}
    all_sentiment_keywords = {sentiment: Counter() for sentiment in SENTIMENT_KEYWORDS.keys()}
    
    total_articles = 0
    financial_articles = 0
    
    for file_path in corpus_files:
        print(f"처리 중: {file_path}")
        texts = load_mudeung_corpus(file_path)
        
        for text in texts:
            if not text.strip():
                continue
                
            total_articles += 1
            
            # 경제/금융 키워드 추출
            financial_keywords = extract_financial_keywords(text)
            sentiment_keywords = extract_sentiment_keywords(text)
            
            # 키워드가 있는 기사만 카운트
            has_financial_keywords = any(keywords for keywords in financial_keywords.values())
            if has_financial_keywords:
                financial_articles += 1
                
                # 카운터에 추가
                for category, keywords in financial_keywords.items():
                    all_financial_keywords[category].update(keywords)
                
                for sentiment, keywords in sentiment_keywords.items():
                    all_sentiment_keywords[sentiment].update(keywords)
    
    # 결과 정리
    dataset = {
        'metadata': {
            'total_articles': total_articles,
            'financial_articles': financial_articles,
            'financial_ratio': financial_articles / total_articles if total_articles > 0 else 0
        },
        'financial_keywords': {
            category: dict(counter.most_common(500))  # 상위 500개로 대폭 확장
            for category, counter in all_financial_keywords.items()
        },
        'sentiment_keywords': {
            sentiment: dict(counter.most_common(200))  # 상위 200개로 대폭 확장
            for sentiment, counter in all_sentiment_keywords.items()
        }
    }
    
    return dataset

def save_lightweight_dataset(dataset: Dict, output_path: str):
    """경량화된 데이터셋 저장"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"데이터셋 저장 완료: {output_path}")
    print(f"총 기사 수: {dataset['metadata']['total_articles']:,}")
    print(f"경제/금융 기사 수: {dataset['metadata']['financial_articles']:,}")
    print(f"경제/금융 기사 비율: {dataset['metadata']['financial_ratio']:.2%}")

def create_impact_ruleset(dataset: Dict) -> Dict[str, str]:
    """영향도 룰셋 생성"""
    impact_rules = {}
    
    # 긍정적 키워드
    positive_keywords = dataset['sentiment_keywords']['positive']
    for keyword, count in positive_keywords.items():
        if count >= 2:  # 2회 이상 등장한 키워드로 기준 더 완화
            impact_rules[keyword] = "긍정적"
    
    # 부정적 키워드
    negative_keywords = dataset['sentiment_keywords']['negative']
    for keyword, count in negative_keywords.items():
        if count >= 2:  # 2회 이상 등장한 키워드로 기준 더 완화
            impact_rules[keyword] = "부정적"
    
    return impact_rules

if __name__ == "__main__":
    # 모두의말뭉치 파일 경로 (사용자가 다운로드한 파일 경로로 수정 필요)
    corpus_files = [
        # 예시 경로 - 실제 파일 경로로 수정 필요
        # "data/mudeung_news_2021.txt",
        # "data/mudeung_news_2022.txt"
    ]
    
    if not corpus_files or not all(os.path.exists(f) for f in corpus_files):
        print("모두의말뭉치 파일을 찾을 수 없습니다.")
        print("다음 단계를 따라주세요:")
        print("1. 모두의말뭉치 신문 데이터를 다운로드")
        print("2. corpus_files 리스트에 실제 파일 경로 입력")
        print("3. 스크립트 재실행")
    else:
        # 데이터셋 생성
        dataset = create_financial_keyword_dataset(corpus_files)
        
        # 경량화된 데이터셋 저장
        save_lightweight_dataset(dataset, "financial_keywords_dataset.json")
        
        # 영향도 룰셋 생성
        impact_rules = create_impact_ruleset(dataset)
        
        # 룰셋 저장
        with open("financial_impact_rules.json", 'w', encoding='utf-8') as f:
            json.dump(impact_rules, f, ensure_ascii=False, indent=2)
        
        print(f"영향도 룰셋 저장 완료: financial_impact_rules.json")
        print(f"총 {len(impact_rules)}개의 영향도 룰 생성") 