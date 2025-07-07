from pymongo import MongoClient
from hashlib import md5

def save_news_to_mongo(news_list, mongo_uri, db_name="news_db", collection="raw_news"):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    for news in news_list:
        # link+published 조합의 해시를 _id로 사용
        unique_str = (news.get("link") or "") + (news.get("published") or "")
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