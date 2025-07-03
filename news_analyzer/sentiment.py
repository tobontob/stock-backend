from transformers import pipeline

# KoBERT 기반 감정분석 파이프라인 (HuggingFace)
sentiment_analyzer = pipeline('sentiment-analysis', model='monologg/koelectra-base-v3-discriminator')

def analyze_sentiment(text):
    try:
        result = sentiment_analyzer(text[:512])  # 입력 길이 제한
        return result[0]['label']
    except Exception as e:
        print(f"[Sentiment ERROR] {e}")
        return None 