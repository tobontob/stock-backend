import pandas as pd
from jinja2 import Template
import random
from typing import Dict, List, Optional

# 키워드 설명 데이터베이스 로드
try:
    desc_db = pd.read_csv('keyword_explain.csv')
except FileNotFoundError:
    # 기본 키워드 설명 데이터 생성
    desc_db = pd.DataFrame({
        '키워드': ['주가', '실적', '투자', '매출', '영업이익', 'M&A', 'R&D', '신제품'],
        '설명': ['주식 가격', '기업 성과', '자본 투입', '매출액', '영업 수익', '기업 합병', '연구개발', '새로운 제품'],
        '영향': ['긍정', '긍정', '긍정', '긍정', '긍정', '긍정', '긍정', '긍정'],
        '업종': ['전 업종', '전 업종', '전 업종', '전 업종', '전 업종', '전 업종', '전 업종', '전 업종']
    })

# 다양한 템플릿 정의
TEMPLATES = {
    'basic': Template("{{company}}의 {{keyword}}는 {{desc}}으로, {{impact}}적 요인입니다."),
    'detailed': Template("{{company}}({{industry}})의 {{keyword}}는 {{desc}}으로, {{impact}}적 영향을 미칠 것으로 예상됩니다."),
    'market_focused': Template("{{company}}의 {{keyword}} 관련 소식은 시장에서 {{impact}}적 반응을 보일 것으로 전망됩니다."),
    'sector_specific': Template("{{industry}} 업종의 {{company}}에서 {{keyword}}는 {{desc}}으로, 업종 내 {{impact}}적 지표로 작용합니다."),
    'trend_analysis': Template("{{company}}의 {{keyword}} 동향은 {{desc}}을 반영하여, {{impact}}적 트렌드로 분석됩니다."),
    'comparative': Template("{{company}}의 {{keyword}}는 {{desc}}으로, 경쟁사 대비 {{impact}}적 위치를 보여줍니다."),
    'future_outlook': Template("{{company}}의 {{keyword}} 전망은 {{desc}}을 고려할 때 {{impact}}적 기대감을 제시합니다."),
    'risk_assessment': Template("{{company}}의 {{keyword}} 관련 리스크는 {{desc}}으로, {{impact}}적 관점에서 평가됩니다.")
}

# 감정별 템플릿 변형
SENTIMENT_TEMPLATES = {
    'positive': {
        'tone': ['긍정적', '호조', '개선', '성장', '상승', '강세'],
        'impact': ['긍정적', '유리한', '호재', '기대감', '낙관적']
    },
    'negative': {
        'tone': ['부정적', '악화', '하락', '위축', '우려', '리스크'],
        'impact': ['부정적', '불리한', '악재', '우려감', '비관적']
    },
    'neutral': {
        'tone': ['중립적', '보합', '안정', '유지', '관망'],
        'impact': ['중립적', '안정적', '보합', '관망', '평온']
    }
}

def extract_keywords(text: str, db_keywords: List[str]) -> List[str]:
    """개선된 키워드 추출 (우선순위 기반)"""
    matched_keywords = []
    
    # 키워드 우선순위 계산
    keyword_scores = {}
    for kw in db_keywords:
        if kw in text:
            score = 0
            # 위치별 점수
            if kw in text[:200]:  # 제목/첫문단
                score += 10
            elif kw in text[:500]:  # 앞부분
                score += 5
            
            # 빈도별 점수
            frequency = text.count(kw)
            score += min(frequency * 2, 10)
            
            # 길이별 점수 (짧은 키워드가 더 구체적)
            if len(kw) <= 3:
                score += 3
            elif len(kw) <= 5:
                score += 2
            
            keyword_scores[kw] = score
    
    # 점수 순으로 정렬하여 상위 키워드 선택
    sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
    return [kw for kw, score in sorted_keywords[:5]]  # 상위 5개만

def generate_fallback_explanation(company_name: str, industry: str, sentiment: str, news_text: str = "") -> str:
    """키워드가 없을 때 기사 맥락을 활용한 기본 설명"""
    # 기사에서 주요 이슈 추출(간단 버전: 제목/첫문단 100자)
    main_issue = news_text[:100] if news_text else ""
    if main_issue:
        if sentiment == 'positive':
            return f"기사 주요 이슈: {main_issue} 이 이슈는 {industry} 업종 및 관련 종목에 긍정적 영향을 줄 수 있습니다."
        elif sentiment == 'negative':
            return f"기사 주요 이슈: {main_issue} 이 이슈는 {industry} 업종 및 관련 종목에 부정적 영향을 줄 수 있습니다."
        else:
            return f"기사 주요 이슈: {main_issue} 이 이슈는 {industry} 업종에 중립적 영향을 줄 수 있습니다."
    # 기존 템플릿(백업)
    fallback_templates = {
        'positive': [
            f"{company_name}의 최근 동향은 {industry} 업종에서 긍정적인 반응을 보이고 있습니다.",
            f"{company_name}의 성과는 {industry} 분야에서 기대감을 제시하고 있습니다.",
            f"{company_name}의 전망은 {industry} 업종 내에서 낙관적으로 분석됩니다."
        ],
        'negative': [
            f"{company_name}의 현재 상황은 {industry} 업종에서 우려감을 나타내고 있습니다.",
            f"{company_name}의 동향은 {industry} 분야에서 주의가 필요한 상황입니다.",
            f"{company_name}의 전망은 {industry} 업종 내에서 신중한 접근이 요구됩니다."
        ],
        'neutral': [
            f"{company_name}의 상황은 {industry} 업종에서 안정적인 모습을 보이고 있습니다.",
            f"{company_name}의 동향은 {industry} 분야에서 관망세를 나타내고 있습니다.",
            f"{company_name}의 전망은 {industry} 업종 내에서 보합세를 유지하고 있습니다."
        ]
    }
    templates = fallback_templates.get(sentiment, fallback_templates['neutral'])
    return random.choice(templates)

def generate_contextual_explanation(news_text: str, company_name: str, industry: str, 
                                  sentiment: str = 'neutral', template_type: str = 'basic') -> str:
    """문맥을 고려한 설명형 분석근거 생성"""
    
    # 키워드 추출
    db_keywords = desc_db['키워드'].tolist()
    matched_keywords = extract_keywords(news_text, db_keywords)
    
    if not matched_keywords:
        return generate_fallback_explanation(company_name, industry, sentiment, news_text)
    
    explanations = []
    used_template = TEMPLATES.get(template_type, TEMPLATES['basic'])
    
    for kw in matched_keywords:
        try:
            row = desc_db[desc_db['키워드'] == kw].iloc[0]
            
            # 업종 필터링
            if row['업종'] != industry and row['업종'] != '전 업종':
                continue
            
            # 감정에 맞는 어조 선택
            sentiment_info = SENTIMENT_TEMPLATES.get(sentiment, SENTIMENT_TEMPLATES['neutral'])
            tone = random.choice(sentiment_info['tone'])
            impact = random.choice(sentiment_info['impact'])
            
            # 템플릿 렌더링
            explanation = used_template.render(
                company=company_name,
                keyword=kw,
                desc=row['설명'],
                impact=impact,
                industry=industry,
                tone=tone
            )
            
            explanations.append(explanation)
            
        except (IndexError, KeyError):
            continue
    
    if explanations:
        return " ".join(explanations)
    else:
        return generate_fallback_explanation(company_name, industry, sentiment, news_text)

def generate_multi_perspective_explanation(news_text: str, company_name: str, industry: str, 
                                         sentiment: str = 'neutral') -> Dict[str, str]:
    """다양한 관점에서의 설명 생성"""
    
    perspectives = {}
    
    # 기본 관점
    perspectives['basic'] = generate_contextual_explanation(
        news_text, company_name, industry, sentiment, 'basic'
    )
    
    # 시장 관점
    perspectives['market'] = generate_contextual_explanation(
        news_text, company_name, industry, sentiment, 'market_focused'
    )
    
    # 업종 관점
    perspectives['sector'] = generate_contextual_explanation(
        news_text, company_name, industry, sentiment, 'sector_specific'
    )
    
    # 트렌드 관점
    perspectives['trend'] = generate_contextual_explanation(
        news_text, company_name, industry, sentiment, 'trend_analysis'
    )
    
    return perspectives

def generate_explanation(news_text: str, company_name: str, industry: str) -> str:
    """기존 함수 호환성을 위한 래퍼"""
    return generate_contextual_explanation(news_text, company_name, industry, 'neutral', 'basic')

# 추가 유틸리티 함수들
def analyze_explanation_quality(explanation: str) -> Dict[str, float]:
    """설명의 품질 분석"""
    quality_metrics = {
        'length': len(explanation),
        'keyword_density': 0.0,
        'sentence_complexity': 0.0
    }
    
    # 키워드 밀도 계산
    if explanation:
        words = explanation.split()
        keyword_count = sum(1 for word in words if len(word) > 2)
        quality_metrics['keyword_density'] = keyword_count / len(words) if words else 0
    
    # 문장 복잡도 계산 (간단한 지표)
    sentences = explanation.split('.')
    quality_metrics['sentence_complexity'] = len(sentences) / max(len(explanation), 1)
    
    return quality_metrics

def enhance_explanation_with_data(explanation: str, additional_data: Dict) -> str:
    """추가 데이터로 설명 강화"""
    if not additional_data:
        return explanation
    
    enhancements = []
    
    if 'sentiment_score' in additional_data:
        score = additional_data['sentiment_score']
        if score > 0.7:
            enhancements.append("강한 긍정적 신호")
        elif score > 0.5:
            enhancements.append("긍정적 신호")
        elif score < -0.5:
            enhancements.append("부정적 신호")
    
    if 'keyword_count' in additional_data:
        count = additional_data['keyword_count']
        if count > 5:
            enhancements.append("다양한 키워드 포함")
        elif count > 2:
            enhancements.append("주요 키워드 포함")
    
    if enhancements:
        return f"{explanation} (추가 분석: {', '.join(enhancements)})"
    
    return explanation 