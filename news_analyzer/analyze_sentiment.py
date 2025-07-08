from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

MODEL_NAME = "snunlp/KR-FinBERT"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
id2label = {0: "neutral", 1: "positive", 2: "negative"}

def analyze_sentiment(text, max_retries=2):
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=1).squeeze().tolist()
            pred_id = int(torch.argmax(logits, dim=1))
            label = id2label[pred_id]
            score = probs[pred_id]
        # reason 생성: 가장 높은 확률의 감정과 신뢰도를 근거로 설명
        reason = f"이 뉴스는 '{label}' 감정으로 분류되었으며, 신뢰도는 {round(score*100, 1)}% 입니다. (확률분포: {probs})"
        return {"label": label, "score": round(score, 4), "probs": probs, "reason": reason}
    except Exception as e:
        print(f"[Sentiment ERROR] {e}")
        return {"label": None, "score": None, "probs": None, "reason": "분석 실패"} 