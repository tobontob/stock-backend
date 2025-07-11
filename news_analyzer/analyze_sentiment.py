from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple

# 기존 KR-FinBERT 모델
MODEL_NAME = "snunlp/KR-FinBERT"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
id2label = {0: "neutral", 1: "positive", 2: "negative"}

# 경량 모델 추가 (메모리 효율적)
LIGHT_MODEL_NAME = "klue/roberta-base"  # 한국어 경량 모델
light_tokenizer = None
light_model = None
light_model_available = False

def load_light_model():
    """경량 모델을 필요시에만 로드하는 함수"""
    global light_tokenizer, light_model, light_model_available
    if light_tokenizer is None:
        try:
            light_tokenizer = AutoTokenizer.from_pretrained(LIGHT_MODEL_NAME)
            light_model = AutoModelForSequenceClassification.from_pretrained(LIGHT_MODEL_NAME)
            light_model_available = True
            print(f"[경량모델] {LIGHT_MODEL_NAME} 로드 완료")
        except Exception as e:
            print(f"[경량모델 로드 실패] {e}")
            light_model_available = False
            return False
    return light_model_available

def analyze_sentiment_with_finbert(text, max_retries=2):
    """기존 KR-FinBERT 모델로 감정 분석"""
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=1).squeeze().tolist()
            pred_id = int(torch.argmax(logits, dim=1))
            label = id2label[pred_id]
            score = probs[pred_id]
        reason = f"KR-FinBERT: '{label}' 감정, 신뢰도 {round(score*100, 1)}%"
        return {"label": label, "score": round(score, 4), "probs": probs, "reason": reason}
    except Exception as e:
        print(f"[FinBERT ERROR] {e}")
        return {"label": None, "score": None, "probs": None, "reason": "FinBERT 분석 실패"}

def analyze_sentiment_with_light_model(text, max_retries=2):
    """경량 모델로 감정 분석"""
    if not load_light_model():
        return {"label": None, "score": None, "probs": None, "reason": "경량모델 로드 실패"}
    
    try:
        inputs = light_tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            outputs = light_model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=1).squeeze().tolist()
            pred_id = int(torch.argmax(logits, dim=1))
            # 경량 모델은 일반적인 감정 레이블 사용
            light_id2label = {0: "negative", 1: "positive"}
            label = light_id2label.get(pred_id, "neutral")
            score = probs[pred_id]
        reason = f"경량모델: '{label}' 감정, 신뢰도 {round(score*100, 1)}%"
        return {"label": label, "score": round(score, 4), "probs": probs, "reason": reason}
    except Exception as e:
        print(f"[경량모델 ERROR] {e}")
        return {"label": None, "score": None, "probs": None, "reason": "경량모델 분석 실패"}

def ensemble_sentiment_analysis(text, max_retries=2):
    """앙상블 방식으로 감정 분석 수행"""
    # FinBERT 분석
    finbert_result = analyze_sentiment_with_finbert(text, max_retries)
    
    # 경량 모델 분석 (가능한 경우에만)
    light_result = None
    if load_light_model():
        light_result = analyze_sentiment_with_light_model(text, max_retries)
    
    # 결과 결합
    results = []
    if finbert_result["label"]:
        results.append(finbert_result)
    if light_result and light_result["label"]:
        results.append(light_result)
    
    if not results:
        return {"label": "neutral", "score": 0.5, "probs": [0.33, 0.33, 0.34], "reason": "모든 모델 분석 실패"}
    
    # 앙상블 로직: 신뢰도가 높은 모델 우선
    best_result = max(results, key=lambda x: x["score"])
    
    # 두 모델 모두 성공한 경우 가중 평균
    if len(results) == 2:
        finbert_weight = 0.7  # 금융 특화 모델에 더 높은 가중치
        light_weight = 0.3
        
        # 레이블 통합 (neutral은 중립으로 처리)
        if finbert_result["label"] == light_result["label"]:
            final_label = finbert_result["label"]
        elif finbert_result["score"] > light_result["score"]:
            final_label = finbert_result["label"]
        else:
            final_label = light_result["label"]
        
        # 가중 평균 점수
        final_score = (finbert_result["score"] * finbert_weight + 
                      light_result["score"] * light_weight)
        
        reason = f"앙상블: {final_label} (FinBERT: {finbert_result['label']}, 경량모델: {light_result['label']})"
    else:
        final_label = best_result["label"]
        final_score = best_result["score"]
        reason = best_result["reason"]
    
    return {
        "label": final_label, 
        "score": round(final_score, 4), 
        "probs": best_result["probs"], 
        "reason": reason
    }

def analyze_sentiment(text, max_retries=2):
    """기존 함수 호환성을 위한 래퍼"""
    return ensemble_sentiment_analysis(text, max_retries) 