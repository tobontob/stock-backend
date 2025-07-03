import re

def clean_news_content(text):
    if not text:
        return None
    # 광고/스팸 패턴 제거 예시
    patterns = [
        r"▶.*?더보기",  # 네이버 더보기 광고
        r"\[.*?기자\]",  # 기자명
        r"무단전재.*?금지",  # 저작권 문구
    ]
    for pat in patterns:
        text = re.sub(pat, "", text)
    # 본문 길이 필터(너무 짧으면 무시)
    if len(text.strip()) < 100:
        return None
    return text.strip() 