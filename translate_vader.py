import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import deepl
from deep_translator import GoogleTranslator
import time
import os

# 설정
current_folder = os.path.dirname(os.path.abspath(__file__))
# 원본 왓챠 리뷰 파일로 변경
file_path = os.path.join(current_folder, 'watcha_korean_SquidGameSeason1_reviews_minimal.csv')
sample_count = 10   # 분석할 개수
deepl_key = ""      # DeepL 키 (없으면 비워두기)

# 데이터 로드
try:
    df = pd.read_csv(file_path, encoding='utf-8')
except:
    df = pd.read_csv(file_path, encoding='cp949')

df.columns = df.columns.str.strip()

# 왓챠 파일은 'review'와 'rating' 컬럼을 사용합니다.
# 결측치 제거
df_kr = df.dropna(subset=['review', 'rating'])

# 지정한 개수만큼 랜덤 추출
if len(df_kr) > sample_count:
    df_kr = df_kr.sample(n=sample_count, random_state=42)

# 분석 및 출력
print(f"\n>>> 왓챠 원본 리뷰 {len(df_kr)}개 번역 및 VADER 점수 비교 시작...")
print(f"{'별점':<6} | {'VADER':<6} | {'VADER가 분석한 영어 번역문 (한글->영어)'}")
print("-" * 100)

analyzer = SentimentIntensityAnalyzer()

for _, row in df_kr.iterrows():
    text = str(row['review'])
    rating = row['rating'] # 5점 만점
    
    # 번역 (DeepL 없으면 구글)
    try:
        if deepl_key:
            translated = deepl.Translator(deepl_key).translate_text(text, target_lang="EN-US").text
        else:
            time.sleep(0.3) # 차단 방지 딜레이
            translated = GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        translated = "Translation Error"

    # VADER 점수 계산 (-1.0 ~ 1.0)
    vader_score = analyzer.polarity_scores(str(translated))['compound']
    
    # 결과 출력
    # 별점은 5점 만점, VADER는 -1~1 사이 점수입니다.
    print(f"{rating:<8} | {vader_score:<8.2f} | {translated.strip()[:80].replace(chr(10), ' ')}...")
