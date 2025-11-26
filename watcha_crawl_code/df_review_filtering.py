import pandas as pd
import re

# 해당 코드는 스포일러방지 리뷰를 필터링하는 기능을 테스트하는 데에 사용된 코드입니다.
# 동일한 기능이 watcha_reviews_crawl.py 파일 내에도 독립된 함수로 구현되어 있습니다.

df = pd.read_csv("./watcha_reviews_csv/watcha_korean_SquidGameSeason1_reviews_minimal.csv")

spoiler_df = df[df['review'] == "스포일러가 있어요!!보기"]

print(f"Spoiler reviews count: {len(spoiler_df)}")
print(spoiler_df)

df.drop(spoiler_df.index, inplace=True)

df.to_csv("./watcha_reviews_csv/watcha_korean_SquidGameSeason1_reviews_minimal.csv", index=False)