import os
from dotenv import load_dotenv
from rss_crawler import fetch_rss_news
from api_crawler import fetch_api_news, fetch_gnews_news, fetch_contextualweb_news, fetch_rss_feed_news, fetch_realtime_news
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

        # 2. API 수집 (newsdata.io, GNews, ContextualWeb, Real-Time News Data, RSS)
        print("[크롤러] API 뉴스 수집 시작")
        api_news = []
        try:
            api_news += fetch_api_news("증권", NEWS_API_KEY)
        except Exception as e:
            print(f"[크롤러] newsdata.io API 뉴스 수집 에러: {e}")
        try:
            api_news += fetch_gnews_news("증권", os.getenv("GNEWS_API_KEY", ""))
        except Exception as e:
            print(f"[크롤러] GNews API 뉴스 수집 에러: {e}")
        try:
            api_news += fetch_contextualweb_news("증권", os.getenv("CONTEXTUALWEB_API_KEY", ""))
        except Exception as e:
            print(f"[크롤러] ContextualWeb API 뉴스 수집 에러: {e}")
        try:
            api_news += fetch_realtime_news("증권", os.getenv("REALTIME_NEWS_API_KEY", ""))
        except Exception as e:
            print(f"[크롤러] Real-Time News Data API 뉴스 수집 에러: {e}")
        try:
            rss_urls = [
                "https://www.mk.co.kr/rss/40300001/",  # 매일경제
                "https://news.naver.com/main/rss/rss.naver?sectionId=101",  # 네이버 경제
                "https://www.hankyung.com/feed/it",  # 한국경제 IT
                "https://www.edaily.co.kr/rss/news.xml",  # 이데일리
                "https://www.yna.co.kr/rss/all",  # 연합뉴스 전체
                "https://biz.chosun.com/site/data/rss/rss.xml",  # 조선비즈
                "https://www.seoul.co.kr/rss/section010100.xml",  # 서울신문 경제
                "https://www.fnnews.com/rss/fn_realnews.xml",  # 파이낸셜뉴스 실시간
                "https://www.etnews.com/news/rss/rss.xml",  # 전자신문
                "https://www.khan.co.kr/rss/rssdata/kh_economy.xml",  # 경향신문 경제
                "https://www.hani.co.kr/rss/economy/",  # 한겨레 경제
                "https://www.mt.co.kr/rss/rss1.xml",  # 머니투데이
                "https://www.sedaily.com/rss/NewsList.xml",  # 서울경제
                "https://www.heraldcorp.com/rss/010000000001.xml",  # 헤럴드경제
                "https://www.munhwa.com/news/section_rss.html?sec=1010",  # 문화일보 경제
                "https://www.kmib.co.kr/rss/rss.asp?sid=eco",  # 국민일보 경제
                "https://www.dt.co.kr/rss/news.xml",  # 디지털타임스
                "https://www.etoday.co.kr/rss/rss.xml",  # 이투데이
                "https://www.sportsseoul.com/news/rss",  # 스포츠서울(경제)
                # 필요시 추가
            ]
            api_news += fetch_rss_feed_news(rss_urls)
        except Exception as e:
            print(f"[크롤러] RSS 피드 뉴스 수집 에러: {e}")
        print(f"[크롤러] API+RSS 뉴스 수집 완료: {len(api_news)}건")
        print(f"[크롤러] API+RSS 뉴스 샘플: {api_news[:2]}")

        # 3. 본문 크롤링 및 정제 (content가 None이거나 'ONLY AVAILABLE IN PAID PLANS'이어도 저장 허용)
        all_news = rss_news + api_news
        print(f"[크롤러] 전체 뉴스 합계: {len(all_news)}건")
        
        # 중복 뉴스 제거 (링크 기준)
        unique_news = {}
        for news in all_news:
            link = news.get("link")
            if link and link not in unique_news:
                unique_news[link] = news
            elif not link:  # 링크가 없는 경우 제목으로 중복 체크
                title = news.get("title")
                if title and title not in [n.get("title") for n in unique_news.values()]:
                    unique_news[f"no_link_{len(unique_news)}"] = news
        
        all_news = list(unique_news.values())
        print(f"[크롤러] 중복 제거 후 뉴스: {len(all_news)}건")
        
        print(f"[크롤러] 전체 뉴스 샘플: {all_news[:2]}")
        print(f"[크롤러] all_news 전체: {all_news}")
        saved_count = 0
        content_success_count = 0
        for news in all_news:
            try:
                content = fetch_news_content(news["link"])
                clean_content = clean_news_content(content)
                # newsdata.io 무료 플랜은 content가 'ONLY AVAILABLE IN PAID PLANS'일 수 있으므로, 이 경우에도 저장
                if clean_content is not None and len(clean_content.strip()) > 50:
                    news["content"] = clean_content
                    content_success_count += 1
                    print(f"[크롤러] 본문 크롤링 성공: {news.get('title')} ({len(clean_content)}자)")
                else:
                    news["content"] = news.get("content")  # 기존 content 유지(혹은 None)
                    print(f"[크롤러] 본문 크롤링 실패: {news.get('title')}")
            except Exception as e:
                print(f"[크롤러] 본문 크롤링 에러: {news.get('link')}, {e}")
                news["content"] = news.get("content")  # 기존 content 유지(혹은 None)
            saved_count += 1
        print(f"[크롤러] 본문 크롤링 성공률: {content_success_count}/{saved_count} ({content_success_count/saved_count*100:.1f}%)")
        print(f"[크롤러] 본문 크롤링 후 전체 뉴스 샘플: {all_news[:5]}")
        print(f"[크롤러] 본문 크롤링 후 content None 개수: {sum(1 for n in all_news if n['content'] is None)}")
        print(f"[크롤러] 본문 크롤링 후 'ONLY AVAILABLE IN PAID PLANS' 개수: {sum(1 for n in all_news if n.get('content') == 'ONLY AVAILABLE IN PAID PLANS')}")

        # 4. MongoDB 저장
        print(f"[크롤러] MongoDB 저장 시작: {saved_count}건")
        print(f"[크롤러] MongoDB 저장 대상 샘플: {all_news[:2]}")
        save_news_to_mongo(all_news, MONGODB_URI)
        print("[크롤러] 뉴스 수집 및 저장 완료")
    except Exception as e:
        import traceback
        print("[크롤러] 전체 예외 발생:", e)
        traceback.print_exc() 