import os
import re
import pandas as pd
import numpy as np

import nltk
from kiwipiepy import Kiwi

from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

import matplotlib.pyplot as plt
from umap import UMAP


# 설정 및 경로
current_folder = os.path.dirname(os.path.abspath(__file__))
kiwi = Kiwi()

# 불용어 설정
# 작품 별로 돌려가면서 추가/수정 필요
STOPWORDS_KR = {
    '오징어', '게임', '오징어게임', '드라마', '영화', '작품', '넷플릭스', '넷플', '시즌',
    '진짜', '정말', '너무', '그냥', '이제', '점', '보고', '봤는데', '하는', '있는', 
    '그리고', '하지만', '그래서', '근데', '이거', '이건', '그게', '생각', '사람', 
    '내용', '정도', '부분', '하나', '건가', '무엇', '어떤', '만큼', '때문', '사실',
    '이다', '하다', '있다', '없다', '되다', '같다', '보다', '보이다', '싶다',
    '나오다', '가다', '오다', '자다', '먹다', '주다', '받다', '알다', '모르다',
    '만들다', '시키다', '우리', '저희', '당신', '그대', '너희', '여러분',
    '평점', '시간', '보기', '스토리', '연출', '배우', '연기', '캐릭터', '한국', '아니다' 
}

domain_stopwords_en = {
    'squid', 'game', 'series', 'show', 'movie', 'netflix', 'season', 'episode',
    'seen', 'time', 'thing', 'make', 'made', 'review', 'acting', 'story', 'plot',
    'character', 'characters', 'end', 'ending', 'good', 'bad', 'great', 'watch', 'watching', 'korean'
}
STOPWORDS_EN = set(ENGLISH_STOP_WORDS) | domain_stopwords_en

# 텍스트 전처리 함수
def preprocess_text(text, lang='KR'):
    if pd.isna(text) or str(text).strip() == "": return ""
    text = str(text)
    
    if lang == 'KR':
        tokens = kiwi.tokenize(text)
        selected_words = []
        for t in tokens:
            if t.tag.startswith('N') or t.tag.startswith('V') or t.tag.startswith('XR'):
                if t.form not in STOPWORDS_KR and len(t.form) > 1:
                    word = t.form + '다' if t.tag.startswith('V') else t.form
                    if word not in STOPWORDS_KR:
                        selected_words.append(word)
        return " ".join(selected_words)
    else:
        # 영어: 소문자 변환 및 정규식 후 불용어 처리
        words = re.findall(r'\b\w+\b', text.lower())
        selected_words = [w for w in words if w not in STOPWORDS_EN and len(w) > 2]
        return " ".join(selected_words)

# 평점 필터링 함수 (극단값만 유지)
def filter_extreme_rating(rating, lang='KR'):
    try:
        r = float(rating)
        if pd.isna(r):
            return np.nan

        if lang == 'KR':
            r = r * 2 # 왓챠는 5점 만점이므로 *2를 해줘서 해외 리뷰와 별점 맞추기
        
        # 4점 이하(혹평) 또는 9점 이상(극찬)만 유효, 나머지는 NaN
        if r <= 4.0 or r >= 9.0:
            return r
        else:
            return np.nan
    except:
        return np.nan

# 데이터 로드 함수
def read_csv_safe(path):
    if not os.path.exists(path):
        print(f"파일 없음: {path}")
        return pd.DataFrame()
    try: return pd.read_csv(path, encoding='utf-8')
    except: 
        try: return pd.read_csv(path, encoding='cp949')
        except: return pd.read_csv(path, encoding='latin1')

# 컬럼 자동 감지
def find_columns_strictly(df):
    cols_lower = {c.lower(): c for c in df.columns}
    # 텍스트 컬럼 찾기
    priority_candidates = ['review', 'text', 'content', 'comment', 'body']
    text_col = None
    for cand in priority_candidates:
        if cand in cols_lower:
            text_col = cols_lower[cand]
            break
    
    # 평점 컬럼 찾기
    rating_candidates = ['rating', 'score', 'star', 'grade']
    rating_col = None
    for cand in rating_candidates:
        for col in df.columns:
            if cand in col.lower():
                rating_col = col
                break
        if rating_col: break
        
    return text_col, rating_col

# 메인 실행 로직
def main():
    print("1. 데이터 로드 중...")
    file_watcha = os.path.join(current_folder, 'watcha_korean_SquidGameSeason1_reviews_minimal.csv')
    file_imdb = os.path.join(current_folder, 'imdb_reviews.csv')

    df_kr = read_csv_safe(file_watcha)
    df_en = read_csv_safe(file_imdb)

    text_col_kr, rating_col_kr = find_columns_strictly(df_kr)
    text_col_en, rating_col_en = find_columns_strictly(df_en)

    processed_data = []

    # 한국어 처리 (Kiwi 문장 분리)
    if text_col_kr and not df_kr.empty:
        for _, row in tqdm(df_kr.iterrows(), total=len(df_kr), desc="Processing Korean"):
            review = str(row.get(text_col_kr, ''))
            raw_rating = row.get(rating_col_kr, None)
            
            # 평점 필터링 (애매한 점수는 NaN 처리)
            trustworthy_rating = filter_extreme_rating(raw_rating, lang='KR')

            if len(review) < 2 or review.lower() == 'nan': continue
            
            # Kiwi 문장 분리
            sentences = kiwi.split_into_sents(review)
            for sent in sentences:
                if len(sent.text) < 10: continue
                clean_tokens = preprocess_text(sent.text, lang='KR')
                if len(clean_tokens.split()) >= 2:
                    processed_data.append({
                        'Original_Sentence': sent.text,
                        'Preprocessed_Tokens': clean_tokens,
                        'Rating': trustworthy_rating, # 필터링된 평점 적용
                        'Lang': 'KR'
                    })

    # 영어 처리 (NLTK 문장 분리)
    if text_col_en and not df_en.empty:
        for _, row in tqdm(df_en.iterrows(), total=len(df_en), desc="Processing English"):
            review = str(row.get(text_col_en, ''))
            raw_rating = row.get(rating_col_en, None)

            trustworthy_rating = filter_extreme_rating(raw_rating, lang='EN')

            if len(review) < 2 or review.lower() == 'nan': continue
            
            # NLTK 문장 분리
            sentences = nltk.sent_tokenize(review)
            for sent in sentences:
                if len(sent) < 10: continue
                clean_tokens = preprocess_text(sent, lang='EN')
                if len(clean_tokens.split()) >= 2:
                    processed_data.append({
                        'Original_Sentence': sent,
                        'Preprocessed_Tokens': clean_tokens,
                        'Rating': trustworthy_rating, # 필터링된 평점 적용
                        'Lang': 'EN'
                    })

    df_final = pd.DataFrame(processed_data)
    print(f"-> 총 분석 대상 문장 수: {len(df_final)}개")

    print("2. 토픽 모델링 수행 중...")
    sentence_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = sentence_model.encode(df_final['Original_Sentence'].tolist(), show_progress_bar=True)
    
    vectorizer_model = CountVectorizer(
        tokenizer=lambda x: x.split(),
        preprocessor=lambda x: x,
        stop_words=list(STOPWORDS_KR | STOPWORDS_EN) 
    )

    # BERTopic 모델 설정
    topic_model = BERTopic(
        embedding_model=sentence_model, 
        vectorizer_model=vectorizer_model,
        min_topic_size=10, 
        nr_topics=15,
        verbose=True
    )

    docs = df_final['Preprocessed_Tokens'].tolist()
    topics, probs = topic_model.fit_transform(docs, embeddings)
    df_final['Topic'] = topics

    # 토픽 이름 매핑
    topic_info = topic_model.get_topic_info()
    df_final['Topic_Name'] = df_final['Topic'].apply(
        lambda x: topic_info[topic_info['Topic'] == x]['Name'].values[0]
    )

    print("3. 결과 저장 중...")
    
    # NaN이 아닌 유효 평점만 사용하여 토픽별 평점 계산
    topic_rating = df_final.groupby('Topic_Name')['Rating'].mean().sort_values()

    # 참고용(실제로 사용하면 안됨)
    print("\n[토픽별 평균 평점 (낮은 순)]")
    print(topic_rating.head(5))
    print("\n[토픽별 평균 평점 (높은 순)]")
    print(topic_rating.tail(5))

    # 저장
    df_final.to_csv(os.path.join(current_folder, "Final_Result_Squid.csv"), index=False, encoding='utf-8-sig')
    topic_rating.to_csv(os.path.join(current_folder, "Topic_Ratings_Squid.csv"), header=True, encoding='utf-8-sig')

    # 대표 예문 저장
    representative_data = []
    for topic_id in sorted(df_final['Topic'].unique()):
        if topic_id == -1: continue 
        
        topic_rows = df_final[df_final['Topic'] == topic_id]
        # 평점이 있는 행 우선, 없으면 전체에서 샘플링
        clean_rows = topic_rows.dropna(subset=['Rating'])
        target_rows = clean_rows if len(clean_rows) >= 5 else topic_rows
            
        samples = target_rows['Original_Sentence'].sample(n=min(5, len(target_rows))).tolist()
        topic_name = topic_info[topic_info['Topic'] == topic_id]['Name'].values[0]
        avg_score = topic_rows['Rating'].mean()
        
        row = {'Topic_ID': topic_id, 'Label': topic_name, 'Avg_Rating': avg_score}
        for i, sent in enumerate(samples):
            row[f'Example_{i+1}'] = sent
        representative_data.append(row)

    pd.DataFrame(representative_data).to_csv(os.path.join(current_folder, "Topic_Examples_Squid.csv"), index=False, encoding='utf-8-sig')
    
    
    # 간단한 산점도 그래프 그리기 (아웃라이어 제외)
    # topic 분포 확인용
    print("4. 토픽 분포 산점도 생성 중 (아웃라이어 제외)...")
    
    # 아웃라이어(-1) 제외
    non_outlier_mask = df_final['Topic'] != -1
    
    # 데이터 필터링
    filtered_embeddings = embeddings[non_outlier_mask]
    filtered_topics = df_final.loc[non_outlier_mask, 'Topic']
    
    if len(filtered_topics) > 0:
        # UMAP을 사용하여 2차원으로 축소 (시각화용)
        # n_neighbors=15, min_dist=0.1 등이 일반적인 파라미터
        umap_2d = UMAP(n_neighbors=15, n_components=2, min_dist=0.1, metric='cosine', random_state=42)
        embeddings_2d = umap_2d.fit_transform(filtered_embeddings)
        
        # 그래프 설정
        plt.figure(figsize=(12, 8))
        
        # 산점도 그리기 (색상은 토픽별로 구분)
        scatter = plt.scatter(
            embeddings_2d[:, 0], 
            embeddings_2d[:, 1], 
            c=filtered_topics, 
            cmap='tab20',  
            s=5,           # 점 크기
            alpha=0.7      # 투명도
        )
        
        # 컬러바 및 레이블 설정
        plt.colorbar(scatter, label='Topic ID')
        plt.title('Topic Clusters Distribution (Outliers Removed)', fontsize=15)
        plt.xlabel('UMAP Dimension 1')
        plt.ylabel('UMAP Dimension 2')
        
        # 파일 저장
        output_img_path = os.path.join(current_folder, "Topic_Scatter_Plot.png")
        plt.savefig(output_img_path, dpi=300, bbox_inches='tight')
        plt.close() # 메모리 해제
        
        print(f"-> 그래프 저장 완료: {output_img_path}")
    else:
        print("-> 유효한 토픽 데이터가 없어 그래프를 그리지 않았습니다.")


if __name__ == "__main__":
    main()
