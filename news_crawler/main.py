import os
from dotenv import load_dotenv
from rss_crawler import fetch_rss_news
from api_crawler import fetch_api_news
from content_crawler import fetch_news_content
from cleaner import clean_news_content
from utils import save_news_to_mongo

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# 1. RSS 수집
rss_urls = [
    "https://www.mk.co.kr/rss/40300001/",
    "https://news.naver.com/main/rss/rss.naver?sectionId=101"
]
rss_news = fetch_rss_news(rss_urls)

# 2. API 수집
api_news = fetch_api_news("증권", NEWS_API_KEY)

# 3. 본문 크롤링 및 정제
all_news = rss_news + api_news
for news in all_news:
    content = fetch_news_content(news["link"])
    clean_content = clean_news_content(content)
    if clean_content:
        news["content"] = clean_content
    else:
        news["content"] = None

# 4. MongoDB 저장
save_news_to_mongo(all_news, MONGODB_URI)
print("뉴스 수집 및 저장 완료") 