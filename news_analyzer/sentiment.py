from transformers import pipeline

print("[sentiment.py] 모델 로딩 시작...")
sentiment_analyzer = pipeline('sentiment-analysis', model='monologg/koelectra-base-v3-discriminator')
print("[sentiment.py] 모델 로딩 완료!")

def analyze_sentiment(text):
    print(f"[analyze_sentiment] 입력 텍스트: {text[:30]}...")
    try:
        result = sentiment_analyzer(text[:512])  # 입력 길이 제한
        print(f"[analyze_sentiment] 결과: {result}")
        return result[0]['label']
    except Exception as e:
        print(f"[Sentiment ERROR] {e}")
        return None 