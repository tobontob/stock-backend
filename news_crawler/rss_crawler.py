import feedparser

def fetch_rss_news(rss_urls):
    news_list = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published
            })
    return news_list 