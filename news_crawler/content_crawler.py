import requests
from bs4 import BeautifulSoup

def fetch_news_content(url):
    try:
        res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        # 네이버 뉴스 예시
        if "naver.com" in url:
            content = soup.select_one("div#newsct_article")
            if content:
                return content.get_text(strip=True)
        # 매일경제 예시
        elif "mk.co.kr" in url:
            content = soup.select_one("div#article_body")
            if content:
                return content.get_text(strip=True)
        # 기타 언론사별 구조 추가 가능
        return None
    except Exception as e:
        print(f"[본문 크롤링 실패] {url} - {e}")
        return None 