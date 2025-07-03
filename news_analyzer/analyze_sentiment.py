import requests
import time

def analyze_sentiment(text, max_retries=2):
    API_URL = "https://jccompany2007-stock-sentiment.hf.space/run/predict/"
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, json={"data": [text]}, timeout=20)
            print("[API RAW RESPONSE]", response.text)  # 응답 내용 확인
            if response.status_code == 200 and response.text.strip():
                result = response.json()
                if "data" in result and result["data"]:
                    return result["data"][0]
            # 응답이 비었거나 올바르지 않으면 재시도
        except Exception as e:
            print(f"[Sentiment API ERROR] {e}")
        # 재시도 전 대기 (슬립 상태 대비)
        time.sleep(3)
    # 모든 시도 실패 시
    return {"label": None, "score": None, "probs": None} 