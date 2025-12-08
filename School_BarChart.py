import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import os

# 1 한글 폰트 설정
if platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='Malgun Gothic') # Windows
plt.rcParams['axes.unicode_minus'] = False


# 2. 데이터 로드 및 전처리

# 파일 경로 (r로 오류 방지)
file_path = r"C:\Users\iyong\.vscode\New folder\School_topic.txt"

if not os.path.exists(file_path):
    print(f"오류: 파일을 찾을 수 없습니다. 경로를 확인해주세요: {file_path}")
else:
    try:
        # 데이터 읽기
        df = pd.read_csv(file_path)

        # 'Lang'으로 되어 있어 'Language'로 그룹화 시 에러
        if 'Lang' in df.columns:
            df = df.rename(columns={'Lang': 'Language'})
        
        # 3 토픽 이름 정의 
        topic_naming = {
            -1: "기타 (미분류)",
            0: "0. 좀비물 장르 특성",
            1: "1. 캐릭터 및 재미",
            2: "2. 학교폭력 및 설정",
            3: "3. 배우 연기력 호평",
            4: "4. 전개 속도 및 분량",
            5: "5. 신파 및 음악(OST)",
            6: "6. 킬링타임용",
            7: "7. 바이러스 기원/설정",
            8: "8. 평점 및 리뷰 언급",
            9: "9. 타 좀비물(킹덤 등) 비교",
            10: "10. 연출력 아쉬움",
            11: "11. 급식실/도서관 액션",
            12: "12. 원작 웹툰 비교",
            13: "13. 고구마(답답한) 전개"
        }
        
        # 토픽 번호를 이름으로 변환하여 Topic_Label 컬럼 생성
        if 'Topic' in df.columns:
            df['Topic_Label'] = df['Topic'].map(topic_naming)
        
        # 4 한국 vs 해외 토픽 비율 계산

        # 4 1) 언어 및 토픽별 리뷰 개수 집계
        topic_counts = df.groupby(['Language', 'Topic_Label']).size().reset_index(name='Count')

        # 4 2) 언어별 총 리뷰 개수 계산 (비율 계산의 분모)
        total_counts_by_lang = df['Language'].value_counts()

        # 4 3) 비율(%) 계산 함수 정의 및 적용
        def calculate_percentage(row):
            lang = row['Language']
            count = row['Count']
            total = total_counts_by_lang[lang]
            return (count / total) * 100

        topic_counts['Percentage'] = topic_counts.apply(calculate_percentage, axis=1)

        # 토픽 레이블 순서 정렬 
        topic_counts = topic_counts.sort_values(by='Topic_Label')

        
        # 5 막대 그래프 시각화
        plt.figure(figsize=(15, 8))

        # Seaborn으로 그룹형 막대 그래프 생성
        bar_plot = sns.barplot(
            data=topic_counts,
            x='Topic_Label',
            y='Percentage',
            hue='Language',
            palette={'KR': '#1f77b4', 'EN': '#ff7f0e'}  # KR: 파랑, EN: 주황
        )

        # 그래프 디자인
        plt.title('지금 우리 학교는: 한국 vs. 해외 리뷰 토픽 비율 비교 분석', fontsize=18, fontweight='bold', pad=20)
        plt.xlabel('리뷰 토픽', fontsize=12)
        plt.ylabel('비율 (%)', fontsize=12)
        plt.xticks(rotation=45, ha='right')  # X축 레이블 45도 회전
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.legend(title='지역', title_fontsize='12')

        # 막대 위에 비율 수치 표시
        for p in bar_plot.patches:
            height = p.get_height()
            if height > 0: # 0보다 큰 경우에만 표시
                bar_plot.text(p.get_x() + p.get_width() / 2., height + 0.5,
                              f'{height:.1f}%', ha="center", fontsize=9)

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"오류 발생: {e}")
