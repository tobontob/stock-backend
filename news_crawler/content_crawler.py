import requests
from bs4 import BeautifulSoup
import re

def fetch_news_content(url):
    try:
        res = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 네이버 뉴스
        if "naver.com" in url:
            content = soup.select_one("div#newsct_article")
            if content:
                return content.get_text(strip=True)
        
        # 매일경제
        elif "mk.co.kr" in url:
            content = soup.select_one("div#article_body")
            if content:
                return content.get_text(strip=True)
        
        # 한국경제
        elif "hankyung.com" in url:
            content = soup.select_one("div.article_body")
            if content:
                return content.get_text(strip=True)
        
        # 이데일리
        elif "edaily.co.kr" in url:
            content = soup.select_one("div#article_body")
            if content:
                return content.get_text(strip=True)
        
        # 연합뉴스
        elif "yna.co.kr" in url:
            content = soup.select_one("div.story-news")
            if content:
                return content.get_text(strip=True)
        
        # 조선일보
        elif "chosun.com" in url:
            content = soup.select_one("div#news_body_id")
            if content:
                return content.get_text(strip=True)
        
        # 중앙일보
        elif "joongang.co.kr" in url:
            content = soup.select_one("div#article_body")
            if content:
                return content.get_text(strip=True)
        
        # 동아일보
        elif "donga.com" in url:
            content = soup.select_one("div#content")
            if content:
                return content.get_text(strip=True)
        
        # 경향신문
        elif "khan.co.kr" in url:
            content = soup.select_one("div#article_content")
            if content:
                return content.get_text(strip=True)
        
        # 한겨레
        elif "hani.co.kr" in url:
            content = soup.select_one("div.text")
            if content:
                return content.get_text(strip=True)
        
        # 서울신문
        elif "seoul.co.kr" in url:
            content = soup.select_one("div#article_content")
            if content:
                return content.get_text(strip=True)
        
        # 국민일보
        elif "kmib.co.kr" in url:
            content = soup.select_one("div#article_content")
            if content:
                return content.get_text(strip=True)
        
        # 디지털타임스
        elif "dt.co.kr" in url:
            content = soup.select_one("div#article_content")
            if content:
                return content.get_text(strip=True)
        
        # 전자신문
        elif "etnews.com" in url:
            content = soup.select_one("div#article_content")
            if content:
                return content.get_text(strip=True)
        
        # 파이낸셜뉴스
        elif "fnnews.com" in url:
            content = soup.select_one("div#article_content")
            if content:
                return content.get_text(strip=True)
        
        # 기타: 일반적인 뉴스 본문 패턴 시도
        else:
            # 일반적인 뉴스 본문 셀렉터들
            selectors = [
                "div.article_body",
                "div#article_body", 
                "div.article-content",
                "div#article_content",
                "div.content",
                "div#content",
                "div.news_content",
                "div#news_content",
                "article",
                "div.story",
                "div.text"
            ]
            
            for selector in selectors:
                content = soup.select_one(selector)
                if content:
                    text = content.get_text(strip=True)
                    # 최소 100자 이상이면 본문으로 인정
                    if len(text) > 100:
                        return text
        
        return None
        
    except Exception as e:
        print(f"[본문 크롤링 실패] {url} - {e}")
        return None 