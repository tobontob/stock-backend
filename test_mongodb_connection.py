import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

def test_mongodb_connection():
    try:
        print("MongoDB 연결 테스트 시작...")
        
        # 연결 설정 (타임아웃 추가)
        client = MongoClient(
            MONGODB_URI, 
            serverSelectionTimeoutMS=30000, 
            socketTimeoutMS=30000,
            connectTimeoutMS=30000
        )
        
        # 연결 테스트
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공!")
        
        # 데이터베이스 및 컬렉션 확인
        db = client["news_db"]
        raw_col = db["raw_news"]
        result_col = db["analyzed_news"]
        
        # 뉴스 개수 확인
        raw_count = raw_col.count_documents({})
        result_count = result_col.count_documents({})
        
        print(f"📊 raw_news 컬렉션: {raw_count}개 문서")
        print(f"📊 analyzed_news 컬렉션: {result_count}개 문서")
        
        # 샘플 데이터 확인
        if raw_count > 0:
            sample_news = raw_col.find_one()
            print(f"📝 샘플 뉴스: {sample_news.get('title', 'No title')}")
            print(f"🔗 링크: {sample_news.get('link', 'No link')}")
            print(f"📄 본문 길이: {len(sample_news.get('content', '')) if sample_news.get('content') else 0}자")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection() 