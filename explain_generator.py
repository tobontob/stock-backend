import pandas as pd
from jinja2 import Template
from konlpy.tag import Okt

# 1. 설명 DB 로딩
desc_db = pd.read_csv('keyword_explain.csv')

# 2. 템플릿 정의
tmpl = Template("{{company}}의 {{keyword}}는 {{desc}}으로, {{impact}}적 요인입니다.")

# 3. 기사에서 키워드 추출 (형태소 분석)
def extract_keywords(text, db_keywords):
    okt = Okt()
    nouns = set(okt.nouns(text))
    # DB에 있는 키워드와 교집합만 추출
    return [kw for kw in db_keywords if kw in nouns]

# 4. 설명 생성 함수
def generate_explanation(news_text, company_name, industry):
    db_keywords = desc_db['키워드'].tolist()
    matched_keywords = extract_keywords(news_text, db_keywords)
    explanations = []
    for kw in matched_keywords:
        row = desc_db[desc_db['키워드'] == kw].iloc[0]
        # 업종이 일치하거나 '전 업종'이면 설명 생성
        if row['업종'] == industry or row['업종'] == '전 업종':
            explanations.append(
                tmpl.render(company=company_name, keyword=kw, desc=row['설명'], impact=row['영향'])
            )
    return " ".join(explanations) if explanations else "핵심 경제/금융 키워드가 발견되지 않았습니다."

# 5. 테스트
if __name__ == "__main__":
    news = "하나금융지주, 최대 실적과 자본비율 상승 기대"
    company = "하나금융지주"
    industry = "금융"
    print(generate_explanation(news, company, industry)) 