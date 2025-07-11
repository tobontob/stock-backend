import re

MARKERS = [
    '관련기사', '함께 본 기사', '인기기사', '추천기사', '주요뉴스', '많이 본 뉴스', '연관기사', '함께보는 기사',
    '댓글', '댓글쓰기', '댓글을 남겨주세요', '의견쓰기'
]

def clean_news_content(text):
    if not text:
        return None
    # 광고/스팸/저작권/기자명/기타 패턴 제거
    patterns = [
        r"▶.*?더보기", r"\[.*?기자\]", r"무단전재.*?금지", r"ⓒ.*?무단전재", r"Copyright.*?All rights reserved",
        r"사진=.*?제공", r"=.*?기자", r"입력.*?수정", r"※.*?무단전재", r"네이버.*?무단전재", r"본 기사.*?무단전재",
        r"[0-9]{4}\. ?[0-9]{2}\. ?[0-9]{2} ?[가-힣]* ?기자",  # 날짜+기자
        r"\(서울=연합뉴스\)", r"\(사진=.*?\)", r"\[.*?=연합뉴스\]"
    ]
    for pat in patterns:
        text = re.sub(pat, "", text)
    # 마커 이후 제거
    for marker in MARKERS:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    # 특수문자/공백 정리
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    # 중복 문장/문단 제거 (간단히)
    lines = text.split('. ')
    seen = set()
    deduped = []
    for line in lines:
        l = line.strip()
        if l and l not in seen:
            deduped.append(l)
            seen.add(l)
    text = '. '.join(deduped)
    if len(text.strip()) < 100:
        return None
    return text.strip() 