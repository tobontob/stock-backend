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