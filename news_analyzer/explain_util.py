import pandas as pd
from jinja2 import Template
from konlpy.tag import Okt

desc_db = pd.read_csv('keyword_explain.csv')
tmpl = Template("{{company}}의 {{keyword}}는 {{desc}}으로, {{impact}}적 요인입니다.")

def extract_keywords(text, db_keywords):
    okt = Okt()
    nouns = set(okt.nouns(text))
    return [kw for kw in db_keywords if kw in nouns]

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