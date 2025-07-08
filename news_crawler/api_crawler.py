import requests

def fetch_api_news(query, api_key):
    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": api_key,
        "q": query,
        "language": "ko",  # 한국어 뉴스만
        "country": "kr",   # 한국 뉴스만
        "category": "business"  # 필요시 카테고리 지정
    }
    res = requests.get(url, params=params)
    print("[크롤러] newsdata.io raw response:", res.text)  # 진단용 전체 응답 출력
    news_list = []
    if res.status_code == 200:
        data = res.json()
        for item in data.get("results", []):
            news_list.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "published": item.get("pubDate"),
                "description": item.get("description")
            })
    else:
        print(f"[API ERROR] {res.status_code} {res.text}")
    return news_list

# GNews API 연동 예시
# https://gnews.io/docs/
def fetch_gnews_news(query, api_key):
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "ko",
        "country": "kr",
        "token": api_key,
        "max": 50
    }
    res = requests.get(url, params=params)
    print("[크롤러] GNews raw response:", res.text)
    news_list = []
    if res.status_code == 200:
        data = res.json()
        for item in data.get("articles", []):
            news_list.append({
                "title": item.get("title"),
                "link": item.get("url"),
                "published": item.get("publishedAt"),
                "description": item.get("description")
            })
    else:
        print(f"[GNews API ERROR] {res.status_code} {res.text}")
    return news_list

# ContextualWeb News API 연동 예시
# https://rapidapi.com/contextualwebsearch/api/websearch/
def fetch_contextualweb_news(query, api_key):
    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }
    params = {
        "q": query,
        "pageNumber": 1,
        "pageSize": 50,
        "autoCorrect": "true",
        "fromPublishedDate": None,
        "toPublishedDate": None
    }
    res = requests.get(url, headers=headers, params=params)
    print("[크롤러] ContextualWeb raw response:", res.text)
    news_list = []
    if res.status_code == 200:
        data = res.json()
        for item in data.get("value", []):
            news_list.append({
                "title": item.get("title"),
                "link": item.get("url"),
                "published": item.get("datePublished"),
                "description": item.get("description")
            })
    else:
        print(f"[ContextualWeb API ERROR] {res.status_code} {res.text}")
    return news_list

# RSS 피드 직접 수집 예시
import feedparser

def fetch_rss_feed_news(rss_urls):
    news_list = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            news_list.append({
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published"),
                "description": entry.get("summary")
            })
    return news_list

def fetch_realtime_news(query, api_key):
    url = "https://real-time-news-data.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "real-time-news-data.p.rapidapi.com"
    }
    params = {
        "query": query,
        "country": "KR",  # 한국 뉴스만
        "language": "ko", # 한국어 뉴스만
        "page": 1
    }
    res = requests.get(url, headers=headers, params=params)
    print("[크롤러] Real-Time News Data API raw response:", res.text)
    news_list = []
    if res.status_code == 200:
        data = res.json()
        for item in data.get("data", []):
            news_list.append({
                "title": item.get("title"),
                "link": item.get("url"),
                "published": item.get("published_datetime_utc"),
                "description": item.get("description")
            })
    else:
        print(f"[Real-Time News API ERROR] {res.status_code} {res.text}")
    return news_list 