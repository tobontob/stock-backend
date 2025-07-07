from pymongo import MongoClient
from hashlib import md5
from dateutil import parser

def save_news_to_mongo(news_list, mongo_uri, db_name="news_db", collection="raw_news"):
    print(f"[크롤러] 저장 대상 뉴스 개수: {len(news_list)}")
    print(f"[크롤러] 저장 대상 뉴스 샘플: {news_list[:2]}")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    for news in news_list:
        # published를 datetime 타입으로 변환
        if isinstance(news.get("published"), str):
            try:
                news["published"] = parser.parse(news["published"])
            except Exception as e:
                print(f"[크롤러] published 날짜 파싱 실패: {news.get('published')}, 에러: {e}")
                # 파싱 실패 시 기존 값 유지
        # link+published 조합의 해시를 _id로 사용
        unique_str = (news.get("link") or "") + (str(news.get("published")) or "")
        news["_id"] = md5(unique_str.encode("utf-8")).hexdigest()
        print(f"[크롤러] 저장 시도: 제목={news.get('title')}, 링크={news.get('link')}, published={news.get('published')}, _id={news['_id']}")
        try:
            result = db[collection].update_one({"_id": news["_id"]}, {"$set": news}, upsert=True)
            if result.upserted_id:
                print(f"[크롤러] 저장 성공(신규): {news.get('title')}")
            else:
                print(f"[크롤러] 중복(이미 존재): {news.get('title')}")
        except Exception as e:
            print(f"[크롤러] 저장 실패: {news.get('title')}, 에러: {e}")

def migrate_published_to_datetime(mongo_uri, db_name="news_db", collection="raw_news"):
    """
    이미 저장된 뉴스의 published 필드를 문자열에서 datetime 타입으로 일괄 변환합니다.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    col = db[collection]
    cursor = col.find({})
    updated = 0
    for doc in cursor:
        pub = doc.get("published")
        if isinstance(pub, str):
            try:
                pub_dt = parser.parse(pub)
                col.update_one({"_id": doc["_id"]}, {"$set": {"published": pub_dt}})
                updated += 1
            except Exception as e:
                print(f"[마이그레이션] published 파싱 실패: {pub}, 에러: {e}")
    print(f"[마이그레이션] 변환 완료: {updated}건 datetime으로 변환됨.") 