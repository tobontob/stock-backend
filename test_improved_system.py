#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 시스템 종합 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_analyzer.main import NewsAnalyzer
from news_analyzer.analyze_sentiment import ensemble_sentiment_analysis
from news_analyzer.explain_util import generate_contextual_explanation, generate_multi_perspective_explanation
from news_analyzer.article_crawler import fetch_article_content
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_news_analyzer():
    """NewsAnalyzer 클래스 테스트"""
    print("=== NewsAnalyzer 클래스 테스트 ===")
    
    try:
        analyzer = NewsAnalyzer()
        print("✅ NewsAnalyzer 초기화 성공")
        print(f"  - 종목 수: {len(analyzer.stock_list)}")
        print(f"  - 긍정 단어 수: {len(analyzer.positive_words)}")
        print(f"  - 부정 단어 수: {len(analyzer.negative_words)}")
        print(f"  - 영향 규칙 수: {len(analyzer.impact_rules)}")
        
        return analyzer
    except Exception as e:
        print(f"❌ NewsAnalyzer 초기화 실패: {e}")
        return None

def test_sentiment_analysis():
    """감정 분석 테스트"""
    print("\n=== 감정 분석 테스트 ===")
    
    test_texts = [
        "삼성전자 실적 호조로 주가 상승세",
        "LG전자 매출 감소로 주가 하락",
        "SK하이닉스 투자 확대로 긍정적 전망",
        "현대차 부도 위기로 시장 우려감 확산",
        "카카오 신제품 출시로 기대감 상승"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n테스트 {i}: {text}")
        try:
            result = ensemble_sentiment_analysis(text)
            print(f"  결과: {result['label']} (신뢰도: {result['score']})")
            print(f"  근거: {result['reason']}")
        except Exception as e:
            print(f"  ❌ 분석 실패: {e}")

def test_stock_extraction(analyzer):
    """종목 추출 테스트"""
    print("\n=== 종목 추출 테스트 ===")
    
    test_texts = [
        "삼성전자의 실적이 호조를 보이며 주가가 상승하고 있습니다.",
        "LG전자와 SK하이닉스의 협력으로 새로운 반도체 기술이 개발되었습니다.",
        "현대차의 신제품 출시로 시장에서 긍정적인 반응을 보이고 있습니다.",
        "카카오의 새로운 서비스가 사용자들에게 호평을 받고 있습니다."
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n테스트 {i}: {text}")
        try:
            stocks = analyzer.extract_stocks_from_text(text, analyzer.stock_list)
            print(f"  추출된 종목: {len(stocks)}개")
            for stock in stocks:
                print(f"    - {stock['name']} ({stock['code']}): 신뢰도 {stock['confidence']}, 위치 {stock['position']}")
        except Exception as e:
            print(f"  ❌ 추출 실패: {e}")

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
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n테스트 케이스 {i}:")
        print(f"  텍스트: {case['text']}")
        print(f"  회사: {case['company']}, 업종: {case['industry']}")
        
        try:
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
        except Exception as e:
            print(f"  ❌ 설명 생성 실패: {e}")

def test_article_crawling():
    """기사 크롤링 테스트"""
    print("\n=== 기사 크롤링 테스트 ===")
    
    # 테스트용 URL (실제로는 존재하는 URL을 사용해야 함)
    test_urls = [
        "https://example.com/test-article-1",
        "https://example.com/test-article-2"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n테스트 {i}: {url}")
        try:
            content = fetch_article_content(url)
            if content:
                print(f"  크롤링 성공: {len(content)}자")
                print(f"  내용 일부: {content[:100]}...")
            else:
                print("  크롤링 실패: 내용을 찾을 수 없음")
        except Exception as e:
            print(f"  ❌ 크롤링 오류: {e}")

def test_analysis_pipeline(analyzer):
    """전체 분석 파이프라인 테스트"""
    print("\n=== 전체 분석 파이프라인 테스트 ===")
    
    test_news = [
        {
            "title": "삼성전자 실적 호조로 주가 상승세",
            "content": "삼성전자가 예상보다 좋은 실적을 발표하여 주가가 상승하고 있습니다. 반도체 부문의 매출 증가가 주요 원인으로 분석됩니다.",
            "link": "https://example.com/samsung-news"
        },
        {
            "title": "LG전자 매출 감소로 주가 하락",
            "content": "LG전자의 최근 실적 발표에서 매출 감소가 확인되어 주가가 하락하고 있습니다. 경기 악화가 주요 원인으로 지적됩니다.",
            "link": "https://example.com/lg-news"
        }
    ]
    
    for i, news in enumerate(test_news, 1):
        print(f"\n테스트 뉴스 {i}: {news['title']}")
        try:
            processed, failed = analyzer.process_news_batch([news])
            print(f"  처리 결과: 성공 {processed}개, 실패 {failed}개")
        except Exception as e:
            print(f"  ❌ 파이프라인 처리 실패: {e}")

def main():
    """메인 테스트 함수"""
    print("개선된 시스템 종합 테스트 시작")
    print("=" * 60)
    
    try:
        # 1. NewsAnalyzer 테스트
        analyzer = test_news_analyzer()
        if not analyzer:
            print("NewsAnalyzer 초기화 실패로 테스트를 중단합니다.")
            return
        
        # 2. 감정 분석 테스트
        test_sentiment_analysis()
        
        # 3. 종목 추출 테스트
        test_stock_extraction(analyzer)
        
        # 4. 설명형 분석근거 생성 테스트
        test_explanation_generation()
        
        # 5. 기사 크롤링 테스트
        test_article_crawling()
        
        # 6. 전체 분석 파이프라인 테스트
        test_analysis_pipeline(analyzer)
        
        print("\n" + "=" * 60)
        print("🎉 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 