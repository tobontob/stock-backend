from pymongo import MongoClient
 
def save_news_to_mongo(news_list, mongo_uri, db_name="news_db", collection="raw_news"):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    for news in news_list:
        db[collection].update_one({"link": news["link"]}, {"$set": news}, upsert=True) 