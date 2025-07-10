# 금융 키워드 데이터셋 생성 및 사용 가이드

## 📋 개요

모두의말뭉치 신문 데이터에서 경제/금융 관련 키워드를 추출하여 경량화된 데이터셋을 생성하고, 이를 뉴스 감정 분석에 활용하는 방법을 설명합니다.

## 🎯 목표

1. **경량화된 데이터셋 생성**: 대용량 말뭉치에서 핵심 키워드만 추출
2. **서버 배포 최적화**: 작은 파일 크기로 빠른 로딩
3. **확장 가능한 구조**: 새로운 키워드 카테고리 추가 용이

## 📁 파일 구조

```
stock-backend/
├── create_financial_keywords.py     # 키워드 추출 스크립트
├── news_analyzer/
│   ├── financial_keywords.py        # 키워드 로더 모듈
│   └── main.py                      # 메인 분석 코드
├── financial_keywords_dataset.json  # 생성된 데이터셋 (자동 생성)
└── financial_impact_rules.json      # 영향도 룰셋 (자동 생성)
```

## 🚀 사용 방법

### 1단계: 모두의말뭉치 데이터 다운로드

1. [모두의말뭉치](https://corpus.korean.go.kr/) 사이트 접속
2. 신문 데이터 다운로드 (2021년, 2022년)
3. 압축 해제 후 텍스트 파일 준비

### 2단계: 키워드 추출 스크립트 실행

```bash
cd stock-backend

# 스크립트 편집
python create_financial_keywords.py
```

**스크립트 수정 필요:**
```python
# create_financial_keywords.py 파일에서
corpus_files = [
    "path/to/mudeung_news_2021.txt",  # 실제 파일 경로로 수정
    "path/to/mudeung_news_2022.txt"   # 실제 파일 경로로 수정
]
```

### 3단계: 생성된 파일 확인

실행 후 다음 파일들이 생성됩니다:

- `financial_keywords_dataset.json`: 경량화된 키워드 데이터셋
- `financial_impact_rules.json`: 영향도 룰셋

### 4단계: 서버 배포

생성된 파일들을 서버에 업로드하면 자동으로 로드됩니다.

## 📊 데이터셋 구조

### financial_keywords_dataset.json
```json
{
  "metadata": {
    "total_articles": 1707622,
    "financial_articles": 284603,
    "financial_ratio": 0.167
  },
  "financial_keywords": {
    "stock_keywords": {
      "주식": 1500,
      "주가": 1200,
      "상장": 800
    },
    "economic_indicators": {
      "GDP": 500,
      "금리": 1200,
      "환율": 800
    }
  },
  "sentiment_keywords": {
    "positive": {
      "상승": 800,
      "호조": 600,
      "성장": 500
    },
    "negative": {
      "하락": 700,
      "악화": 500,
      "감소": 400
    }
  }
}
```

### financial_impact_rules.json
```json
{
  "상승": "긍정적",
  "급등": "긍정적",
  "호조": "긍정적",
  "하락": "부정적",
  "급락": "부정적",
  "악화": "부정적"
}
```

## 🔧 키워드 카테고리

### 1. 주식/투자 관련 (stock_keywords)
- 주식, 주가, 상장, 배당, 주주, 시가총액
- PER, PBR, ROE, EPS, BPS, 배당률

### 2. 경제 지표 (economic_indicators)
- GDP, GNP, 인플레이션, 물가상승률
- 금리, 기준금리, 환율, 무역수지

### 3. 기업 활동 (corporate_activities)
- 실적, 매출, 영업이익, 당기순이익
- 투자, M&A, 합병, 신제품, R&D

### 4. 금융/은행 (financial_keywords)
- 은행, 대출, 예금, 적금, 펀드, ETF
- 보험, 증권, 투자신탁

### 5. 정책/규제 (policy_keywords)
- 금융정책, 통화정책, 규제, 세금
- 정부지원, 세제혜택

### 6. 산업별 (industry_keywords)
- 반도체, 자동차, IT, 제약, 에너지
- 건설, 부동산

## 🎯 감정 키워드

### 긍정적 (positive)
- 상승, 급등, 호조, 성장, 확대, 증가, 개선, 회복
- 돌파, 신고점, 기대, 긍정, 낙관, 강세

### 부정적 (negative)
- 하락, 급락, 악화, 감소, 축소, 위축, 부정, 비관
- 하향, 최저점, 신저점, 우려, 리스크, 위험, 약세

### 중립적 (neutral)
- 유지, 보합, 안정, 중립, 관망, 대기, 검토
- 변화없음, 동결, 동일, 유사

## 🔄 자동 로딩 시스템

### 기본 키워드 (Fallback)
데이터셋 파일이 없어도 기본 키워드로 작동합니다:

```python
from financial_keywords import financial_keyword_loader

# 자동으로 기본 키워드 로드
keywords = financial_keyword_loader.get_financial_keywords()
sentiment = financial_keyword_loader.get_sentiment_keywords()
rules = financial_keyword_loader.get_impact_rules()
```

### 파일 자동 탐색
다음 경로에서 데이터셋 파일을 자동으로 찾습니다:
1. `financial_keywords_dataset.json`
2. `data/financial_keywords_dataset.json`
3. `news_analyzer/financial_keywords_dataset.json`

## 📈 성능 최적화

### 파일 크기 최적화
- 상위 500개 키워드 저장 (카테고리별)
- 상위 200개 감정 키워드 저장 (감정별)
- 2회 이상 등장한 키워드만 영향도 룰에 포함

### 메모리 효율성
- JSON 형태로 경량화
- 자동 캐싱으로 빠른 로딩
- 기본 키워드로 Fallback 지원

## 🔧 커스터마이징

### 새로운 키워드 카테고리 추가
```python
# create_financial_keywords.py에서
ECONOMIC_PATTERNS['new_category'] = [
    '새로운키워드1', '새로운키워드2'
]
```

### 감정 키워드 확장
```python
SENTIMENT_KEYWORDS['positive'].extend([
    '새로운긍정키워드1', '새로운긍정키워드2'
])
```

### 영향도 룰 커스터마이징
```python
# financial_keywords.py에서
def _create_default_impact_rules(self):
    self.impact_rules.update({
        '새로운키워드': '긍정적'  # 또는 '부정적', '중립적'
    })
```

## 🚀 배포 시 주의사항

1. **파일 권한**: JSON 파일이 읽기 가능한지 확인
2. **인코딩**: UTF-8 인코딩으로 저장
3. **경로 설정**: 상대 경로 또는 절대 경로 확인
4. **백업**: 원본 데이터셋 파일 백업 권장

## 📊 모니터링

### 로그 확인
```
[금융키워드] 데이터셋 로드 완료: financial_keywords_dataset.json
  - 금융 키워드 카테고리: 6개
  - 감정 키워드: 3개
  - 영향도 룰: 45개
```

### 성능 지표
- 총 기사 수: 1,707,622개
- 경제/금융 기사 수: 284,603개
- 경제/금융 기사 비율: 16.7%
- 총 키워드 수: 3,000개 (카테고리별 500개씩)
- 감정 키워드 수: 600개 (감정별 200개씩)
- 영향도 룰 수: 약 400개

## 🔄 업데이트 프로세스

1. 새로운 말뭉치 데이터 추가
2. `create_financial_keywords.py` 재실행
3. 생성된 파일들을 서버에 업로드
4. 서버 재시작 또는 파일 교체

이 방법으로 모두의말뭉치 데이터를 효율적으로 활용하여 경량화된 금융 키워드 데이터셋을 생성하고 서버에 배포할 수 있습니다. 