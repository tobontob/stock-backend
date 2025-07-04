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
        return {"label": label, "score": round(score, 4), "probs": probs}
    except Exception as e:
        print(f"[Sentiment ERROR] {e}")
        return {"label": None, "score": None, "probs": None} 