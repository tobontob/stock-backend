import requests
import os

def fetch_api_news(query, api_key):
    url = "https://news-api.korea.ac.kr/v1/search"
    params = {"query": query, "sort": "latest", "apiKey": api_key}
    res = requests.get(url, params=params)
    news_list = []
    if res.status_code == 200:
        for item in res.json().get("articles", []):
            news_list.append({
                "title": item["title"],
                "link": item["url"],
                "published": item["publishedAt"]
            })
    return news_list 