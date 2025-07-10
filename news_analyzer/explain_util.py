import pandas as pd
from jinja2 import Template

desc_db = pd.read_csv('keyword_explain.csv')
tmpl = Template("{{company}}의 {{keyword}}는 {{desc}}으로, {{impact}}적 요인입니다.")

def extract_keywords(text, db_keywords):
    # 형태소 분석 없이 단순 포함 체크
    return [kw for kw in db_keywords if kw in text]

def generate_explanation(news_text, company_name, industry):
    db_keywords = desc_db['키워드'].tolist()
    matched_keywords = extract_keywords(news_text, db_keywords)
    explanations = []
    for kw in matched_keywords:
        row = desc_db[desc_db['키워드'] == kw].iloc[0]
        if row['업종'] == industry or row['업종'] == '전 업종':
            explanations.append(
                tmpl.render(company=company_name, keyword=kw, desc=row['설명'], impact=row['영향'])
            )
    return " ".join(explanations) if explanations else None 