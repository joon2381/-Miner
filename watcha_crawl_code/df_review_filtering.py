import pandas as pd

# 해당 코드는 스포일러방지 리뷰를 필터링하는 기능을 테스트하는 데에 사용된 코드입니다.
# 동일한 기능이 watcha_reviews_crawl.py 파일 내에도 독립된 함수로 구현되어 있습니다.

MOVIE_TITLE_LIST = ["폭싹 속았수다", "오징어 게임 시즌 1"]
MOVIE_TITLE_EN_LIST = ["When Life Gives You Tangerines", "Squid Game Season 1"]

for MOVIE_TITLE, MOVIE_TITLE_EN in zip(MOVIE_TITLE_LIST, MOVIE_TITLE_EN_LIST) :
    df = pd.read_csv(f"./watcha_reviews_csv/watcha_korean_{MOVIE_TITLE_EN.replace(' ', '')}_reviews_minimal.csv")

    spoiler_df = df[df['review'] == "스포일러가 있어요!!보기"]

    print(f"Spoiler reviews count: {len(spoiler_df)}")
    print(spoiler_df)

    df.drop(spoiler_df.index, inplace=True)

    df.to_csv(f"./watcha_reviews_csv/watcha_korean_{MOVIE_TITLE_EN.replace(' ', '')}_reviews_minimal.csv", index=False)