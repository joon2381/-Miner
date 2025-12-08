import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 1 환경 설정 및 데이터 로드

# 한글 폰트 설정 (Windows 기준 'Malgun Gothic', Mac은 'AppleGothic')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

#어두운 배경 테마 적용
plt.style.use('dark_background')

# 파일 경로 
file_name = r"C:\Users\iyong\.vscode\New folder\School_topic.txt"


# 2 토픽 이름 (지금 우리 학교는)
topic_naming = {
    -1: "기타 (미분류)",
    0: "0. 좀비 장르/완성도 평가",
    1: "1. 캐릭터/로맨스 답답함",
    2: "2. 학교폭력/선정성 논란",
    3: "3. 신인 배우 연기력 호평",
    4: "4. 전개 속도/분량(지루함)",
    5: "5. 신파/억지 감동 비판",
    6: "6. 킬링타임용 재미",
    7: "7. 바이러스 기원 설정",
    8: "8. 평점/리뷰 반응",
    9: "9. 타 작품(킹덤 등) 비교",
    10: "10. 연출력/감독 역량",
    11: "11. 급식실/도서관 액션",
    12: "12. 원작 웹툰과 비교",
    13: "13. 발암 유발/고구마 전개"
}


# 3 데이터 처리 및 시각화 로직

try:
    df = pd.read_csv(file_name)
    
    # 데이터 전처리
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Topic'] = pd.to_numeric(df['Topic'], errors='coerce')
    valid_data = df[(df['Topic'] != -1) & (df['Rating'].notnull())].copy()

    # 토픽별 통계 계산
    topic_stats = valid_data.groupby(['Topic'])['Rating'].agg(['mean', 'count']).reset_index()
    topic_stats.columns = ['Topic', 'Average_Rating', 'Review_Count']
    topic_stats['Topic_Label'] = topic_stats['Topic'].map(topic_naming)
    
    # 강점/약점 기준 점수는 데이터 분포에 맞춰 조정
    # 전체 평점이 낮아서 기준을 6.0 / 4.0으로 설정
    HIGH_THRESHOLD = 6.0  
    LOW_THRESHOLD = 4.0

    # 버블 색상 설정 
    colors = []
    for rating in topic_stats['Average_Rating']:
        if rating >= HIGH_THRESHOLD:
            colors.append('lime')  # 강점 (초록)
        elif rating < LOW_THRESHOLD:
            colors.append('red')   # 약점 (빨강)
        else:
            colors.append('gray')  # 중립 (회색)

    
    # 4 시각화: 버블 차트 
    fig, ax = plt.subplots(figsize=(14, 9))

    # 1) 배경 영역 설정 (강점/단점 Zone 표시)
    ax.axhspan(0, LOW_THRESHOLD, color='darkred', alpha=0.2, label=f'Weakness Zone (< {LOW_THRESHOLD})')
    ax.axhspan(HIGH_THRESHOLD, 10, color='darkgreen', alpha=0.2, label=f'Strength Zone (> {HIGH_THRESHOLD})')
    
    # 기준선 생성
    ax.axhline(y=LOW_THRESHOLD, color='red', linestyle='--', linewidth=1, alpha=0.7)
    ax.axhline(y=HIGH_THRESHOLD, color='lime', linestyle='--', linewidth=1, alpha=0.7)

    # 2) 버블 차트 생성 (크기 = 리뷰 수 * 가중치)
    scatter = ax.scatter(
        topic_stats['Review_Count'],
        topic_stats['Average_Rating'],
        s=topic_stats['Review_Count'] * 3,  # 버블 크기 확대
        c=colors,
        alpha=0.8,
        edgecolors='white',
        linewidth=1.5
    )

    # 3) 토픽 이름 생성
    for idx, row in topic_stats.iterrows():
        # 리뷰 수가 적은 토픽은 글씨를 작게, 중요 토픽은 크게/진하게 표시
        is_important = (row['Review_Count'] > 100) or (row['Average_Rating'] >= HIGH_THRESHOLD) or (row['Average_Rating'] < LOW_THRESHOLD)
        font_weight = 'bold' if is_important else 'normal'
        font_size = 11 if is_important else 9
        label_text = row['Topic_Label'].split('.')[1].strip() if '.' in str(row['Topic_Label']) else str(row['Topic_Label'])

        # 텍스트가 버블에 가리지 않도록 위치 조정
        offset_y = 0.15 if row['Average_Rating'] > 5 else -0.25
        
        ax.annotate(
            label_text,
            (row['Review_Count'], row['Average_Rating'] + offset_y),
            fontsize=font_size,
            color='white',
            weight=font_weight,
            ha='center'
        )

    # 4) 최종 그래프 꾸미기
    ax.set_title('[지금 우리 학교는] 토픽별 영향력 및 감성 분석', fontsize=20, color='white', pad=20)
    ax.set_xlabel('리뷰 수 (Topic Volume)', fontsize=14, color='white')
    ax.set_ylabel('평균 평점 (Sentiment Rating)', fontsize=14, color='white')
    
    # 축 범위 및 스타일 설정
    ax.set_ylim(0, 10.5)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

    # 범례들 표시
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label=f'Strength (> {HIGH_THRESHOLD})', markerfacecolor='lime', markersize=10),
        Line2D([0], [0], marker='o', color='w', label=f'Neutral ({LOW_THRESHOLD}-{HIGH_THRESHOLD})', markerfacecolor='gray', markersize=10),
        Line2D([0], [0], marker='o', color='w', label=f'Weakness (< {LOW_THRESHOLD})', markerfacecolor='red', markersize=10)
    ]
    ax.legend(handles=legend_elements, loc='upper right', facecolor='black', edgecolor='white')

    plt.grid(True, linestyle=':', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 스타일 원상복구 (추후 다른 그래프 영향 방지)
    plt.style.use('default')

except FileNotFoundError:
    print(f"오류: '{file_name}' 파일을 찾을 수 없습니다.")
