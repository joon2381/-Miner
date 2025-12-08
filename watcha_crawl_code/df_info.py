import re
import pandas as pd

# 해당 코드는 csv 파일로 저장된 각 영화 리뷰 크롤링 DataFrame 정보를 출력하는 데에 사용된 코드입니다.

MOVIE_TITLE_LIST = ["폭싹 속았수다", "오징어 게임 시즌 1",
                    "오징어 게임 시즌 2", "오징어 게임 시즌 3",
                    "더 글로리 파트 1", "더 글로리 파트 2", 
                    "이상한 변호사 우영우", "기생충",
                    "지금 우리 학교는 시즌 1", "부산행",
                    "설국열차", "D.P. 시즌 1",
                    "D.P. 시즌 2", "경성크리처 시즌 1",
                    "경성크리처 시즌 2", "킹더랜드",
                    "택배기사", "야차", "카터"]
MOVIE_TITLE_EN_LIST = ["When Life Gives You Tangerines", "Squid Game Season 1",
                       "Squid Game Season 2", "Squid Game Season 3",
                       "The Glory Part 1", "The Glory Part 2", 
                       "Extraordinary Attorney Woo", "Parasite",
                       "All of Us Are Dead Season 1", "Train to Busan",
                       "Snowpiercer", "D.P. Season 1",
                       "D.P. Season 2", "Gyeongseong Creature Season 1",
                       "Gyeongseong Creature Season 2", "King The Land",
                       "Black Knight", "Yaksha: Ruthless Operations", "Carter"]

for MOVIE_TITLE, MOVIE_TITLE_EN in zip(MOVIE_TITLE_LIST, MOVIE_TITLE_EN_LIST) :
    df = pd.read_csv(f"./watcha_reviews_csv/watcha_korean_{re.sub(r'[^a-zA-Z0-9가-힣.]', '', MOVIE_TITLE_EN)}_reviews_minimal.csv")

    print(f"Movie Title: {MOVIE_TITLE} ({MOVIE_TITLE_EN})\n DataFrame Info:")
    df.info()
    print()