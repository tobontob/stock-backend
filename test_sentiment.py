#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
감성사전 로딩 테스트 스크립트
"""

import os
import glob
import pandas as pd

def load_knu_sentilex():
    """KNU 감성사전 로딩 테스트"""
    # 여러 경로에서 SentiWord_Dict.txt 파일 자동 탐색
    search_paths = [
        'SentiWord_Dict.txt',  # 현재 디렉토리
        '../SentiWord_Dict.txt',  # 상위 디렉토리
        '../../SentiWord_Dict.txt',  # 상위 상위 디렉토리
        'KnuSentiLex*/**/SentiWord_Dict.txt',  # KnuSentiLex 폴더 내
        '**/SentiWord_Dict.txt'  # 모든 하위 폴더
    ]
    
    candidates = []
    for pattern in search_paths:
        if '*' in pattern:
            candidates.extend(glob.glob(pattern, recursive=True))
        else:
            if os.path.exists(pattern):
                candidates.append(pattern)
    
    if not candidates:
        print('[감성사전 경고] SentiWord_Dict.txt 파일을 찾을 수 없습니다.')
        return set(), set()
    
    path = candidates[0]
    print(f'[감성사전] 파일 발견: {path}')
    
    try:
        # 헤더가 없는 형식이므로 컬럼명을 직접 지정
        df = pd.read_csv(path, sep='\t', encoding='utf-8', header=None, names=['word', 'polarity'])
        pos_words = set(df[df['polarity'] > 0]['word'])
        neg_words = set(df[df['polarity'] < 0]['word'])
        print(f'[감성사전] 긍정 {len(pos_words)}개, 부정 {len(neg_words)}개 단어 로딩 완료')
        
        # 샘플 출력
        print(f'\n=== 긍정 단어 샘플 (처음 10개) ===')
        for i, word in enumerate(list(pos_words)[:10]):
            print(f"{i+1}. {word}")
        
        print(f'\n=== 부정 단어 샘플 (처음 10개) ===')
        for i, word in enumerate(list(neg_words)[:10]):
            print(f"{i+1}. {word}")
        
        return pos_words, neg_words
    except Exception as e:
        print(f'[감성사전 로딩 오류] {e}')
        return set(), set()

if __name__ == "__main__":
    print("=== 감성사전 로딩 테스트 ===")
    positive_words, negative_words = load_knu_sentilex()
    
    if positive_words and negative_words:
        print("✅ 감성사전 로딩 성공!")
    else:
        print("❌ 감성사전 로딩 실패!")
    
    print("=== 테스트 완료 ===") 