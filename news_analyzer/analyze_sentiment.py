import requests

def analyze_sentiment(text):
    API_URL = "https://huggingface.co/spaces/jccompany2007/stock-sentiment/api/predict/"
    try:
        response = requests.post(API_URL, json={"data": [text]}, timeout=10)
        result = response.json()
        return result["data"][0]  # label, score, probs 포함
    except Exception as e:
        print(f"[Sentiment API ERROR] {e}")
        return {"label": None, "score": None, "probs": None} 