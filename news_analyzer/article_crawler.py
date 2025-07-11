import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

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

UNWANTED_SELECTORS = [
    '.relate_news', '.popular_news', '.ad_section', '.news_list', '.news_more', '.news-aside',
    '.article-aside', '.article_relation', '.article_recommend', '.article_bottom', '.article_comment',
    '.article_footer', '.copyright', '.sns_area', '.tag_area', '.recommend', '.related', '.relation_news',
    '.news_link', '.news_sponsor', '.news_copyright', '.news_ad', '.ad_box', '.ad', '.banner',
    '#relate_news', '#popular_news', '#ad_section', '#news_list', '#news_more', '#news-aside',
    '#article-aside', '#article_relation', '#article_recommend', '#article_bottom', '#article_comment',
    '#article_footer', '#copyright', '#sns_area', '#tag_area', '#recommend', '#related', '#relation_news',
    '#news_link', '#news_sponsor', '#news_copyright', '#news_ad', '#ad_box', '#ad', '#banner'
]

MARKERS = [
    '관련기사', '함께 본 기사', '인기기사', '추천기사', '주요뉴스', '많이 본 뉴스', '연관기사', '함께보는 기사',
    '댓글', '댓글쓰기', '댓글을 남겨주세요', '의견쓰기'
]

def clean_news_content(text):
    """기사 본문 정제 함수"""
    if not text:
        return None
    # 광고/스팸/저작권/기자명/기타 패턴 제거
    patterns = [
        r"▶.*?더보기", r"\[.*?기자\]", r"무단전재.*?금지", r"ⓒ.*?무단전재", r"Copyright.*?All rights reserved",
        r"사진=.*?제공", r"=.*?기자", r"입력.*?수정", r"※.*?무단전재", r"네이버.*?무단전재", r"본 기사.*?무단전재",
        r"[0-9]{4}\. ?[0-9]{2}\. ?[0-9]{2} ?[가-힣]* ?기자",  # 날짜+기자
        r"\(서울=연합뉴스\)", r"\(사진=.*?\)", r"\[.*?=연합뉴스\]"
    ]
    for pat in patterns:
        text = re.sub(pat, "", text)
    # 마커 이후 제거
    for marker in MARKERS:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    # 특수문자/공백 정리
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    # 중복 문장/문단 제거 (간단히)
    lines = text.split('. ')
    seen = set()
    deduped = []
    for line in lines:
        l = line.strip()
        if l and l not in seen:
            deduped.append(l)
            seen.add(l)
    text = '. '.join(deduped)
    if len(text.strip()) < 100:
        return None
    return text.strip()

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
                for unwanted in UNWANTED_SELECTORS:
                    for tag in content.select(unwanted):
                        tag.decompose()
                text = content.get_text(separator=' ', strip=True)
                text = clean_news_content(text)
                if text and len(text) > 100:
                    return text
        # fallback: 가장 긴 div/p
        candidates = []
        for tag in soup.find_all(['div', 'p']):
            text = tag.get_text(separator=' ', strip=True)
            text = clean_news_content(text)
            if text and len(text) > 100:
                candidates.append((len(text), text))
        if candidates:
            candidates.sort(reverse=True)
            return candidates[0][1]
        return None
    except Exception as e:
        print(f"[크롤링 실패] {url} - {e}")
        return None 