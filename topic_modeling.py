import pandas as pd
import numpy as np
import os
import re
import nltk
from nltk.tokenize import sent_tokenize
from bertopic import BERTopic
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.representation import KeyBERTInspired
from konlpy.tag import Okt
from kiwipiepy import Kiwi
from tqdm import tqdm


# 데이터 로드
current_folder = os.path.dirname(os.path.abspath(__file__))
file_watcha = os.path.join(current_folder, 'watcha_korean_SquidGameSeason1_reviews_minimal.csv')
file_imdb = os.path.join(current_folder, 'imdb_reviews.csv')

def read_csv_safe(path):
    try: return pd.read_csv(path, encoding='utf-8')
    except: return pd.read_csv(path, encoding='cp949')

df_kr = read_csv_safe(file_watcha)
df_en = read_csv_safe(file_imdb)

# 문장 분리기 (속도 빠른 Kiwi 사용)
kiwi = Kiwi()

# 문장 분리 & 점수 선별
# 점수는 극단적인 경우(10점, 5점 이하)만 남기고 나머지는 None 처리
print("1. 데이터 전처리 및 문장 분리 중...")

all_data = []

# 한국어 처리
# df_kr = df_kr.iloc[:1000] # 테스트용, 실전에서는 주석 처리

for idx, row in tqdm(df_kr.iterrows(), total=len(df_kr), desc="KR (Kiwi)"):
    review = str(row['review'])
    # 왓챠 5점 만점 -> 10점 만점으로 환산
    org_score = float(row.get('score', 0)) * 2 
    
    # 10점 or 5점 이하는 점수 부여, 나머지는 None(빈칸)
    if org_score == 10 or org_score <= 5:
        filtered_score = org_score
    else:
        filtered_score = None  
        
    try:
        # Kiwi로 문장 분리
        splits = [s.text for s in kiwi.split_into_sents(review)]
    except:
        splits = review.split('\n')
    
    for s in splits:
        s = s.strip()
        if len(s) >= 4: # 너무 짧은 문장 제외
            all_data.append({
                'Review_ID': f"KR_{idx}",
                'Source': 'KR',
                'Sentence': s,
                'Original_Rating': org_score,    # 참고용 원본
                'Rating_Filtered': filtered_score # 분석용 (조건부 점수)
            })

# (2) 영어 처리
for idx, row in tqdm(df_en.iterrows(), total=len(df_en), desc="EN (NLTK)"):
    review = str(row['review'])
    org_score = float(row.get('rating', 0))
    
    # 영어도 동일한 로직 적용
    if org_score == 10 or org_score <= 5:
        filtered_score = org_score
    else:
        filtered_score = None
        
    splits = sent_tokenize(review)
    for s in splits:
        s = s.strip()
        if len(s) >= 10: # 영어는 좀 더 길게 잡음
            all_data.append({
                'Review_ID': f"EN_{idx}",
                'Source': 'EN',
                'Sentence': s,
                'Original_Rating': org_score,
                'Rating_Filtered': filtered_score
            })

df_all = pd.DataFrame(all_data)
print(f"   => 총 {len(df_all)}개 문장 준비 완료.")

# 2. BERTopic 모델링 (토픽 수 30, 작품에 따라 조정)
print("2. 토픽 모델링 수행 중... (토픽 수: 30개)")

okt = Okt()

# 명사만 추출하여 키워드 품질 높이기
class CustomTokenizer:
    def __init__(self, okt):
        self.okt = okt
    def __call__(self, text):
        if re.search('[가-힣]', text):
            # 2글자 이상 명사만 추출
            return [n for n in self.okt.nouns(text) if len(n) >= 2]
        else:
            text = re.sub(r'[^\w\s]', '', text).lower()
            return [w for w in text.split() if len(w) >= 3]

# 불용어
# 작품별로 진행해가면서 필요시 추가
stop_words = [
    'movie', 'series', 'drama', 'film', 'netflix', 'squid', 'game', 
    '영화', '드라마', '오징어', '게임', '넷플릭스', '작품', '시즌', 'season',
    '진짜', '정말', '너무', '그냥', '사람', '생각', '정도', '느낌', 'review', 'watching',
    'episode', 'ep', 'thing', 'time', 'show', 'watch', 'story', 'plot',
    '보고', '봤는데', '하는', '있는', '그리고', '하지만', '근데', '많이'
]

vectorizer_model = CountVectorizer(tokenizer=CustomTokenizer(okt), stop_words=stop_words, token_pattern=None)

hdbscan_model = HDBSCAN(min_cluster_size=15, min_samples=5, prediction_data=True, gen_min_span_tree=True)

topic_model = BERTopic(
    embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
    vectorizer_model=vectorizer_model,
    representation_model=KeyBERTInspired(),
    nr_topics=30,        # 30개 토픽으로 설정
    verbose=True
)

# 학습
topics, probs = topic_model.fit_transform(df_all['Sentence'].tolist())

print("아웃라이어 재할당 중...")

# strategy="embeddings": 문장의 의미(벡터)를 기반으로 가장 가까운 토픽을 찾습니다.
# threshold=0.6: 유사도가 60% 이상인 확실한 경우만 구조하고, 나머지는 버립니다. 
# (너무 낮추면 엉뚱한 곳에 들어갑니다. 0.5 ~ 0.6 추천)
new_topics = topic_model.reduce_outliers(
    df_all['Sentence'].tolist(), 
    topics, 
    strategy="embeddings", 
    threshold=0.6 
)

# 토픽 정보 갱신
topic_model.update_topics(df_all['Sentence'].tolist(), topics=new_topics)
topics = new_topics
df_all['Topic'] = topics

# 3. 결과 정리 및 저장
print("3. 결과 파일 생성 중...")

df_all['Topic'] = topics

# 토픽 이름 생성 (자동)
topic_labels = topic_model.generate_topic_labels(nr_words=3, topic_prefix=False, separator='_')
topic_model.set_topic_labels(topic_labels)

# 토픽 라벨 매핑 (에러 방지 로직 포함)
topic_info = topic_model.get_topic_info()
id_to_label = {}
if 'CustomLabel' in topic_info.columns:
    id_to_label = dict(zip(topic_info['Topic'], topic_info['CustomLabel']))
elif topic_model.custom_labels_ is not None:
    # 수동 매핑
    for i, label in enumerate(topic_model.custom_labels_):
        # BERTopic 내부 인덱싱 보정 (-1 토픽이 0번째일 수 있음)
        topic_id = topic_info.iloc[i]['Topic'] 
        id_to_label[topic_id] = label
else:
    id_to_label = dict(zip(topic_info['Topic'], topic_info['Name']))

df_all['Topic_Label'] = df_all['Topic'].map(id_to_label)

# 전체 데이터 CSV 저장
save_path_csv = os.path.join(current_folder, "Final_Result.csv")
df_all.to_csv(save_path_csv, index=False, encoding='utf-8-sig')


# 대표 문장 추출 (토픽 이름 지을 때 참고용)
print("4. 사람이 분석하기 쉽도록 '대표 문장' 추출 중...")

repr_data = []

# 각 토픽별로 반복
for topic_id in sorted(list(set(topics))):
    if topic_id == -1: continue # 아웃라이어(노이즈)는 제외

    # 현재 자동 생성된 라벨
    current_label = id_to_label.get(topic_id, f"Topic {topic_id}")
    
    # 대표 문장 가져오기 (BERTopic이 해당 토픽과 가장 유사도가 높은 문장을 찾아줌)
    rep_docs = topic_model.get_representative_docs(topic_id)
    
    # 딕셔너리 생성
    row_dict = {
        'Topic_ID': topic_id,
        'Auto_Label': current_label,
        'Your_Custom_Name': '' # 이곳에 직접 토픽 이름 넣기
    }
    
    # 문장 5개까지 채워넣기
    for i in range(5):
        if i < len(rep_docs):
            row_dict[f'Example_Sentence_{i+1}'] = rep_docs[i]
        else:
            row_dict[f'Example_Sentence_{i+1}'] = ""
            
    repr_data.append(row_dict)

# 대표 문장 CSV 저장
df_repr = pd.DataFrame(repr_data)
save_path_repr = os.path.join(current_folder, "Topic_Representative_Sentences.csv")
df_repr.to_csv(save_path_repr, index=False, encoding='utf-8-sig')


# 간단한 산점도 분포 시각화
# 실제는 더 좋은 퀄리티의 시각화 따로 진행해야함
try:
    # 데이터가 많으면 2만개 샘플링
    viz_docs = df_all['Sentence'].tolist()
    if len(viz_docs) > 20000:
        import random
        viz_docs = random.sample(viz_docs, 20000)
    
    fig = topic_model.visualize_documents(viz_docs, custom_labels=True)
    fig.write_html(os.path.join(current_folder, "Final_Scatter.html"))
except Exception as e:
    print(f"시각화 저장 건너뜀: {e}")

print("\n" + "="*60)
print("다음 파일들을 확인")
print(f"1. 전체 데이터: {save_path_csv}")
print("-" * 60)
print(f"2. 토픽 이름 짓기용 파일: {save_path_repr}")
print("-" * 60)
print(f"3. 산점도: {os.path.join(current_folder, 'Final_Scatter.html')}")
print("="*60)
