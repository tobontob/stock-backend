import os
from dotenv import load_dotenv
from rss_crawler import fetch_rss_news
from api_crawler import fetch_api_news
from content_crawler import fetch_news_content
from cleaner import clean_news_content
from utils import save_news_to_mongo

if __name__ == "__main__":
    try:
        print("[크롤러] main.py 시작")
        load_dotenv()

        MONGODB_URI = os.getenv("MONGODB_URI")
        NEWS_API_KEY = os.getenv("NEWS_API_KEY")

        # 1. RSS 수집
        rss_urls = [
            "https://www.mk.co.kr/rss/40300001/",
            "https://news.naver.com/main/rss/rss.naver?sectionId=101"
        ]
        print("[크롤러] RSS 뉴스 수집 시작")
        rss_news = fetch_rss_news(rss_urls)
        print(f"[크롤러] RSS 뉴스 수집 완료: {len(rss_news)}건")
        print(f"[크롤러] RSS 뉴스 샘플: {rss_news[:2]}")

        # 2. API 수집
        print("[크롤러] API 뉴스 수집 시작")
        try:
            api_news = fetch_api_news("증권", NEWS_API_KEY)
            print(f"[크롤러] API 뉴스 수집 완료: {len(api_news)}건")
            print(f"[크롤러] API 뉴스 샘플: {api_news[:2]}")
        except Exception as e:
            print(f"[크롤러] API 뉴스 수집 에러: {e}")
            api_news = []

        # 3. 본문 크롤링 및 정제
        all_news = rss_news + api_news
        print(f"[크롤러] 전체 뉴스 합계: {len(all_news)}건")
        print(f"[크롤러] 전체 뉴스 샘플: {all_news[:2]}")
        saved_count = 0
        for news in all_news:
            content = fetch_news_content(news["link"])
            clean_content = clean_news_content(content)
            if clean_content:
                news["content"] = clean_content
            else:
                news["content"] = None
            saved_count += 1

        # 4. MongoDB 저장
        print(f"[크롤러] MongoDB 저장 시작: {saved_count}건")
        print(f"[크롤러] MongoDB 저장 대상 샘플: {all_news[:2]}")
        save_news_to_mongo(all_news, MONGODB_URI)
        print("[크롤러] 뉴스 수집 및 저장 완료")
    except Exception as e:
        import traceback
        print("[크롤러] 전체 예외 발생:", e)
        traceback.print_exc() 