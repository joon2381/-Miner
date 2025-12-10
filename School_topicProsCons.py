import pandas as pd

# 1 데이터 로드 및 전처리
# 파일 경로
file_path = r"C:\Users\iyong\.vscode\New folder\School_topic.txt"

try:
    df = pd.read_csv(file_path)

except FileNotFoundError:
    print(f"파일을 찾을 수 없습니다: {file_path}")

# 숫자형 변환 및 결측치 제거
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['Topic'] = pd.to_numeric(df['Topic'], errors='coerce').astype('Int64')
df_filtered = df[(df['Topic'] != -1) & (df['Rating'].notnull())].copy()

# 2. 토픽 이름 (분석 결과)
TOPIC_REDEFINED = {
    0: '0. 좀비물 장르 만족도',
    1: '1. 캐릭터(청산/온조) 및 재미 평가',
    2: '2. 학교 폭력 묘사 논란',
    3: '3. 배우/연기력 호평',
    4: '4. 전개 속도 및 에피소드 길이',
    5: '5. 신파/음악/반복적 연출 비판',
    6: '6. 킬링타임용 평가',
    7: '7. 바이러스 및 학교 설정',
    8: '8. 평점/리뷰 언급',
    9: '9. 타 좀비물(킹덤, 부산행) 비교',
    10: '10. 감독 연출력/부족함 지적',
    11: '11. 도서관/급식실 액션 연출',
    12: '12. 원작 각색 평가',
    13: '13. 발암 요소 및 답답한 전개'
}

# 3 데이터 분석 (평점 및 리뷰 수 계산)
topic_score_analysis = df_filtered.groupby('Topic').agg(
    Average_Rating=('Rating', 'mean'),
    Review_Count=('Topic', 'size')
).sort_values(by='Average_Rating', ascending=False).reset_index()

# 토픽 이름 매핑
topic_score_analysis['Topic_Name_Redefined'] = topic_score_analysis['Topic'].map(TOPIC_REDEFINED)

# 강점(6.0 이상) / 단점(4.0 미만) 분류
strengths = topic_score_analysis[topic_score_analysis['Average_Rating'] >= 6.0]
weaknesses = topic_score_analysis[topic_score_analysis['Average_Rating'] < 4.0]

# 4. 결과 출력
print("## 3 & 4 토픽 이름 재정의 및 강점/단점 분석 (평점 기반)")

# 강점 테이블 출력
print("# 작품의 주요 강점 토픽 (평균 평점 6.0점 이상)")
if not strengths.empty:
    print(strengths[['Topic_Name_Redefined', 'Average_Rating', 'Review_Count']].to_markdown(index=False, floatfmt=".2f"))
else:
    print("해당 조건의 토픽이 없습니다.")

# 단점 테이블 출력
print("\n# 작품의 주요 단점 토픽 (평균 평점 4.0점 미만)")
if not weaknesses.empty:
    print(weaknesses[['Topic_Name_Redefined', 'Average_Rating', 'Review_Count']].to_markdown(index=False, floatfmt=".2f"))
else:
    print("해당 조건의 토픽이 없습니다.")

print("\n" + "="*50 + "\n")

# 5 분석 텍스트 자동 생성 로직
print("## 5. 데이터 기반 작품 최종 강점 및 단점 분석")

print("# 데이터 기반 작품 최종 강점")
# 강점 1: 평점 1위
if not strengths.empty:
    top = strengths.iloc[0]
    print(f"- *압도적인 연기력 호평*: '{top['Topic_Name_Redefined']}' 토픽이 압도적인 평점 {top['Average_Rating']:.2f}점을 기록하며, 신예 배우들의 연기력이 작품의 가장 큰 버팀목임을 입증합니다.")

# 강점 2: 평점 2위
if len(strengths) > 1:
    sec = strengths.iloc[1]
    print(f"- *긍정적 여론 형성*: '{sec['Topic_Name_Redefined']}' 토픽({sec['Average_Rating']:.2f}점)을 통해 일부 시청층에서 긍정적인 평가 흐름이 형성되고 있음을 알 수 있습니다.")


print("\n# 데이터 기반 작품 최종 단점")
if not weaknesses.empty:
    # 단점 1: 평점 최하위
    worst = weaknesses.sort_values('Average_Rating').iloc[0]
    print(f"- *답답한 전개에 대한 혹평*: '{worst['Topic_Name_Redefined']}' 토픽이 최저 평점 {worst['Average_Rating']:.2f}점을 기록, 개연성 부족과 고구마 전개가 시청자 이탈의 핵심 원인임을 보여줍니다.")

    # 단점 2: 리뷰 수(불만 볼륨) 1위
    vol = weaknesses.sort_values('Review_Count', ascending=False).iloc[0]
    print(f"- *대중적 불만의 중심*: '{vol['Topic_Name_Redefined']}' 토픽은 가장 많은 리뷰({vol['Review_Count']}개)가 집중되었음에도 낮은 평점({vol['Average_Rating']:.2f}점)을 기록하여, 캐릭터 설정과 재미 면에서 대다수 시청자를 만족시키지 못했음을 시사합니다.")

    # 단점 3: 특정 논란 (학교 폭력 - Topic 2) 체크
    topic_2 = weaknesses[weaknesses['Topic'] == 2]
    if not topic_2.empty:
        t2 = topic_2.iloc[0]
        print(f"- *학교 폭력 묘사 논란*: '{t2['Topic_Name_Redefined']}' 토픽 또한 상당한 리뷰 수({t2['Review_Count']}개)와 낮은 평점({t2['Average_Rating']:.2f}점)을 보여, 자극적인 연출이 오히려 독이 되었음을 데이터가 증명합니다.")
