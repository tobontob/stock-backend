import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

ARTICLE_SELECTORS = {
    'hankyung.com': ['.article-body', '.art_read', '#articletxt'],
    'mk.co.kr': ['#article_body', '.art_txt'],
    'chosun.com': ['.par', '.article-body', '#news_body_id'],
    'joongang.co.kr': ['.article_body', '.article_content', '#article_body'],
    'yna.co.kr': ['#articleWrap', '.article-text', '.story-news', '#articleBody'],
    'news.naver.com': ['#dic_area', '.newsct_article', '#articeBody'],
    'news.daum.net': ['#harmonyContainer', '.article_view', '.news_view'],
    'sedaily.com': ['.article_view', '#v_article'],
    'edaily.co.kr': ['.news_body', '#articleBody'],
    'mt.co.kr': ['#textBody', '.view_text'],
    'hankookilbo.com': ['.article-body', '.art_txt'],
    'hani.co.kr': ['#a-left-scroll-in', '.article-text', '#article_view_headline', '#article_view_headline2'],
    'khan.co.kr': ['.art_body', '#articleBody'],
    'newsis.com': ['#textBody', '.view_text'],
    'biz.chosun.com': ['.article-body', '.par'],
    'heraldcorp.com': ['.article_txt', '#articleText'],
    'fnnews.com': ['#article_content', '.article_txt'],
    'seoul.co.kr': ['#atic_txt1', '.article-text'],
    'donga.com': ['.article_txt', '#articleBody'],
    'munhwa.com': ['#articleBody', '.article_txt'],
    'segye.com': ['#article_txt', '.article_txt'],
    'ohmynews.com': ['.article_view', '#article_text'],
    # 필요시 추가
}

def get_domain(url):
    return urlparse(url).netloc.replace('www.', '')

def fetch_article_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        domain = get_domain(url)
        selectors = ARTICLE_SELECTORS.get(domain, [])
        for selector in selectors:
            content = soup.select_one(selector)
            if content and len(content.get_text(strip=True)) > 50:
                return content.get_text(separator=' ', strip=True)
        # fallback: 가장 긴 div/p
        candidates = []
        for tag in soup.find_all(['div', 'p']):
            text = tag.get_text(separator=' ', strip=True)
            if len(text) > 100:
                candidates.append((len(text), text))
        if candidates:
            candidates.sort(reverse=True)
            return candidates[0][1]
        return None
    except Exception as e:
        print(f"[크롤링 실패] {url} - {e}")
        return None 