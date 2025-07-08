import pandas as pd
import requests
from io import StringIO
import re

print("=== 종목 추출 로직 테스트 ===")

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

# 테스트용 뉴스 데이터
test_news = [
    {
        "title": "삼성전자, 반도체 시장 회복세로 실적 개선",
        "content": "삼성전자가 최근 반도체 시장의 회복세를 바탕으로 실적이 개선되고 있다. 특히 메모리 반도체 부문에서 호조를 보이고 있으며, SK하이닉스와 함께 글로벌 시장에서 경쟁력을 확보하고 있다."
    },
    {
        "title": "LG전자, AI 가전 시장 진출 확대",
        "content": "LG전자가 인공지능(AI) 기술을 활용한 스마트 가전 시장 진출을 확대하고 있다. 삼성전자와 경쟁하며 시장 점유율을 높이고 있다."
    },
    {
        "title": "현대차, 전기차 시장에서 급성장",
        "content": "현대차가 전기차 시장에서 급성장하고 있다. 기아와 함께 국내 자동차 업계를 이끌고 있으며, 글로벌 시장에서도 경쟁력을 확보하고 있다."
    },
    {
        "title": "일반적인 경제 뉴스",
        "content": "오늘 주식 시장이 전반적으로 상승세를 보이고 있다. 투자자들의 관심이 높아지고 있으며, 경제 전망이 밝아지고 있다."
    }
]

print("\n=== 테스트 뉴스 분석 ===")
for i, news in enumerate(test_news, 1):
    print(f"\n--- 테스트 뉴스 {i} ---")
    text = news["title"] + " " + news["content"]
    related_stocks = extract_stocks_from_text(text, stock_list)
    print(f"제목: {news['title']}")
    print(f"추출된 종목: {related_stocks}")

print("\n=== 테스트 완료 ===") 