#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KNU 감성사전 자동 다운로드 스크립트
"""

import requests
import os
import zipfile
import shutil

def download_knu_lexicon():
    """KNU 감성사전 다운로드"""
    
    # KNU 감성사전 다운로드 URL (실제 URL로 수정 필요)
    url = "https://raw.githubusercontent.com/park1200656/KnuSentiLex/master/data/SentiWord_Dict.txt"
    
    try:
        print("KNU 감성사전 다운로드 중...")
        
        # 파일 다운로드
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 파일 저장
        with open("SentiWord_Dict.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print("KNU 감성사전 다운로드 완료: SentiWord_Dict.txt")
        print(f"파일 크기: {len(response.text)} bytes")
        
        return True
        
    except Exception as e:
        print(f"KNU 감성사전 다운로드 실패: {e}")
        print("기본 감성사전을 생성합니다...")
        
        # 기본 감성사전 생성
        create_default_lexicon()
        return False

def create_default_lexicon():
    """기본 감성사전 생성"""
    
    default_lexicon = """# KNU 감성사전 기본 버전
# 형식: 단어\t극성\t강도
# 극성: 1(긍정), -1(부정), 0(중립)
# 강도: 1~5 (1: 약함, 5: 강함)

# 긍정적 단어들
상승\t1\t5
급등\t1\t5
호조\t1\t4
성장\t1\t4
확대\t1\t4
증가\t1\t3
개선\t1\t3
회복\t1\t3
돌파\t1\t5
신고점\t1\t5
최고점\t1\t5
기대\t1\t3
긍정\t1\t4
낙관\t1\t4
강세\t1\t4
투자유치\t1\t4
성과\t1\t3
실적호조\t1\t4
매출증가\t1\t3
이익증가\t1\t3
배당증가\t1\t3
수익성장\t1\t4
고성장\t1\t4
급성장\t1\t5
성장세\t1\t4
호전\t1\t3
개선세\t1\t3
회복세\t1\t3
상승세\t1\t4
강세세\t1\t4
돌파세\t1\t5
급등세\t1\t5
신기록\t1\t5
최고치\t1\t5
기대감\t1\t3
낙관론\t1\t4
긍정론\t1\t4
강세론\t1\t4
상승론\t1\t4

# 부정적 단어들
하락\t-1\t5
급락\t-1\t5
악화\t-1\t4
감소\t-1\t3
축소\t-1\t3
위축\t-1\t3
부정\t-1\t4
비관\t-1\t4
하향\t-1\t4
최저점\t-1\t5
신저점\t-1\t5
우려\t-1\t3
리스크\t-1\t4
위험\t-1\t4
약세\t-1\t4
실적악화\t-1\t4
손실\t-1\t4
적자\t-1\t4
부도\t-1\t5
파산\t-1\t5
청산\t-1\t4
폐업\t-1\t4
하락세\t-1\t4
약세세\t-1\t4
악화세\t-1\t4
감소세\t-1\t3
축소세\t-1\t3
위축세\t-1\t3
부정세\t-1\t4
비관세\t-1\t4
우려세\t-1\t3
리스크세\t-1\t4
위험세\t-1\t4
하향세\t-1\t4
최저치\t-1\t5
신저치\t-1\t5
부정론\t-1\t4
비관론\t-1\t4
약세론\t-1\t4
하락론\t-1\t4

# 중립적 단어들
유지\t0\t2
보합\t0\t2
안정\t0\t2
중립\t0\t2
관망\t0\t2
대기\t0\t2
검토\t0\t2
검토중\t0\t2
변화없음\t0\t2
동결\t0\t2
동일\t0\t2
유사\t0\t2
비슷\t0\t2
일정\t0\t2
안정세\t0\t2
보합세\t0\t2
유지세\t0\t2
중립세\t0\t2
관망세\t0\t2
대기세\t0\t2
검토세\t0\t2
안정론\t0\t2
보합론\t0\t2
유지론\t0\t2
중립론\t0\t2
관망론\t0\t2
대기론\t0\t2
검토론\t0\t2
안정성\t0\t2
보합성\t0\t2
유지성\t0\t2
중립성\t0\t2
관망성\t0\t2
대기성\t0\t2
검토성\t0\t2
변화성\t0\t2
"""
    
    try:
        with open("SentiWord_Dict.txt", "w", encoding="utf-8") as f:
            f.write(default_lexicon)
        
        print("기본 감성사전 생성 완료: SentiWord_Dict.txt")
        print(f"파일 크기: {len(default_lexicon)} bytes")
        return True
        
    except Exception as e:
        print(f"기본 감성사전 생성 실패: {e}")
        return False

if __name__ == "__main__":
    print("=== KNU 감성사전 다운로드 시작 ===")
    
    # 다운로드 시도
    success = download_knu_lexicon()
    
    if success:
        print("✅ KNU 감성사전 다운로드 성공")
    else:
        print("⚠️ 기본 감성사전 사용")
    
    print("=== 완료 ===") 