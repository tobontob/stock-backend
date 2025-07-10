#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 분석 시스템 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_analyzer.analyze_sentiment import ensemble_sentiment_analysis, analyze_sentiment_with_finbert, analyze_sentiment_with_light_model
from news_analyzer.explain_util import generate_contextual_explanation, generate_multi_perspective_explanation
from news_analyzer.financial_keywords import FinancialKeywordLoader

def test_sentiment_analysis():
    """감정 분석 테스트"""
    print("=== 감정 분석 테스트 ===")
    
    test_texts = [
        "삼성전자 실적 호조로 주가 상승세",
        "LG전자 매출 감소로 주가 하락",
        "SK하이닉스 투자 확대로 긍정적 전망",
        "현대차 부도 위기로 시장 우려감 확산",
        "카카오 신제품 출시로 기대감 상승"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n테스트 {i}: {text}")
        
        # 앙상블 분석
        ensemble_result = ensemble_sentiment_analysis(text)
        print(f"  앙상블 결과: {ensemble_result['label']} (신뢰도: {ensemble_result['score']})")
        print(f"  근거: {ensemble_result['reason']}")
        
        # 개별 모델 분석
        finbert_result = analyze_sentiment_with_finbert(text)
        print(f"  FinBERT: {finbert_result['label']} (신뢰도: {finbert_result['score']})")
        
        light_result = analyze_sentiment_with_light_model(text)
        print(f"  경량모델: {light_result['label']} (신뢰도: {light_result['score']})")

def test_explanation_generation():
    """설명형 분석근거 생성 테스트"""
    print("\n=== 설명형 분석근거 생성 테스트 ===")
    
    test_cases = [
        {
            "text": "삼성전자의 실적이 호조를 보이며 주가가 상승하고 있습니다.",
            "company": "삼성전자",
            "industry": "전자업",
            "sentiment": "positive"
        },
        {
            "text": "LG전자의 매출 감소로 인해 주가가 하락하고 있습니다.",
            "company": "LG전자", 
            "industry": "전자업",
            "sentiment": "negative"
        },
        {
            "text": "SK하이닉스의 투자 확대로 긍정적인 전망이 나오고 있습니다.",
            "company": "SK하이닉스",
            "industry": "반도체",
            "sentiment": "positive"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n테스트 케이스 {i}:")
        print(f"  텍스트: {case['text']}")
        print(f"  회사: {case['company']}, 업종: {case['industry']}")
        
        # 기본 설명 생성
        basic_explanation = generate_contextual_explanation(
            case['text'], case['company'], case['industry'], case['sentiment'], 'basic'
        )
        print(f"  기본 설명: {basic_explanation}")
        
        # 다중 관점 설명 생성
        multi_explanations = generate_multi_perspective_explanation(
            case['text'], case['company'], case['industry'], case['sentiment']
        )
        print(f"  다중 관점:")
        for perspective, explanation in multi_explanations.items():
            print(f"    {perspective}: {explanation}")

def test_financial_keywords():
    """금융 키워드 분석 테스트"""
    print("\n=== 금융 키워드 분석 테스트 ===")
    
    # 키워드 로더 초기화
    keyword_loader = FinancialKeywordLoader()
    
    test_texts = [
        "삼성전자의 주가가 상승하며 실적 호조를 보이고 있습니다. 투자 확대로 인해 매출이 증가했습니다.",
        "LG전자의 주가가 하락하며 매출 감소로 인한 실적 악화가 우려됩니다.",
        "SK하이닉스의 R&D 투자 확대로 신제품 개발이 활발히 진행되고 있습니다."
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n테스트 {i}: {text}")
        
        # 금융 키워드 추출
        financial_keywords = keyword_loader.extract_financial_keywords_from_text(text)
        print(f"  금융 키워드: {financial_keywords}")
        
        # 감정 키워드 추출
        sentiment_keywords = keyword_loader.extract_sentiment_keywords_from_text(text)
        print(f"  감정 키워드: {sentiment_keywords}")
        
        # 영향도 점수
        impact_score = keyword_loader.get_impact_score(text)
        print(f"  영향도 점수: {impact_score}")

def test_stock_extraction():
    """종목 추출 테스트"""
    print("\n=== 종목 추출 테스트 ===")
    
    # 간단한 종목 리스트 (테스트용)
    test_stock_list = [
        {"회사명": "삼성전자", "종목코드": "005930", "업종": "전자업"},
        {"회사명": "LG전자", "종목코드": "066570", "업종": "전자업"},
        {"회사명": "SK하이닉스", "종목코드": "000660", "업종": "반도체"},
        {"회사명": "현대차", "종목코드": "005380", "업종": "자동차"},
        {"회사명": "카카오", "종목코드": "035420", "업종": "IT"}
    ]
    
    test_texts = [
        "삼성전자의 실적이 호조를 보이며 주가가 상승하고 있습니다.",
        "LG전자와 SK하이닉스의 협력으로 새로운 반도체 기술이 개발되었습니다.",
        "현대차의 신제품 출시로 시장에서 긍정적인 반응을 보이고 있습니다."
    ]
    
    from news_analyzer.main import extract_stocks_from_text
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n테스트 {i}: {text}")
        
        extracted_stocks = extract_stocks_from_text(text, test_stock_list)
        print(f"  추출된 종목: {extracted_stocks}")
        
        for stock in extracted_stocks:
            print(f"    - {stock['name']} ({stock['code']}): 신뢰도 {stock['confidence']}, 위치 {stock['position']}")

def main():
    """메인 테스트 함수"""
    print("개선된 분석 시스템 테스트 시작")
    print("=" * 50)
    
    try:
        # 1. 감정 분석 테스트
        test_sentiment_analysis()
        
        # 2. 설명형 분석근거 생성 테스트
        test_explanation_generation()
        
        # 3. 금융 키워드 분석 테스트
        test_financial_keywords()
        
        # 4. 종목 추출 테스트
        test_stock_extraction()
        
        print("\n" + "=" * 50)
        print("모든 테스트 완료!")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 