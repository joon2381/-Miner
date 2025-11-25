import time, re

import pandas as pd

from collections import Counter

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from konlpy.tag import Okt

# 왓챠피디아 아이디
USER_ID = "lgr9603@kangwon.ac.kr"
USER_PWD = "lgr2618409!"

# 검색할 영화명
"""
** 주의점 **
영화명을 검색한 뒤 가장 처음 검색 결과로 나온 영화의 리뷰를 크롤링하므로 영화 제목의 오탈자에 주의할 것
"""
MOVIE_TITLE = "폭싹 속았수다"

# 화면 스크롤 횟수
COUNT = 10

# koNLPy 를 사용한 빈도수 추출
"""
여러 문자열 리스트(strings)를 받아 자주 등장하는 단어(빈도순)와 단어별 가중치(등장 횟수)를 반환.
:param strings: 문자열 리스트
:param top_n: 등장 횟수 상위 n개만 리턴 (None 인 경우 전체 리턴)
:return: [(단어, 등장횟수), ...] 형태의 리스트
"""
def konlpy(strings, top_n=None) :
    nouns = []
    okt = Okt()

    for text in strings :
        for noun in okt.nouns(text) :
            nouns.append(noun)
    # Trouble Shooting **Done**
    # print(nouns)
    try :
        counter = Counter(nouns)
    except Exception as e:
        print(e)
        return None
    if top_n :
        return counter.most_common(top_n)
    else :
        return counter.most_common()

# 단어별 빈도수 추출
"""
여러 문자열 리스트(strings)를 받아 자주 등장하는 단어(빈도순)와 단어별 가중치(등장 횟수)를 반환합니다.
:param strings: 문자열의 리스트
:param top_n: 상위 N개만 리턴하고 싶을 때 (None이면 전체)
:return: [(단어, 등장횟수), ...] 형태의 리스트
"""
def get_word_frequencies(strings, top_n=None):
    words = []
    for s in strings:
        # 소문자로 변환 후, 단어만 추출 (영어 기준, 한글은 \w에 포함)
        words += re.findall(r'\w+', s.lower())
    counter = Counter(words)
    if top_n:
        return counter.most_common(top_n)
    else:
        return counter.most_common()

# 팝업 광고 제거
"""
:param driver: selenium webdriver 객체
"""
def delete_ad(drive) :
    try :
        drive.find_element(By.CSS_SELECTOR, 'div.WelcomeDisplayModal > div:nth-of-type(2) > button:nth-of-type(2)').click()
        drive.implicitly_wait(100)
    except Exception as e :
        print(f"{e} : pop-up ad page not found")
        pass

# 크롬 드라이버로 네이버 열기
URL = 'https://naver.com'
driver = webdriver.Chrome()
driver.get(url=URL)
driver.implicitly_wait(100)

# 네이버에서 왓챠피디아 입력해서 들어가기
search = driver.find_element(By.CSS_SELECTOR, '#query')
search_content = "왓챠피디아"
search.send_keys(search_content)
driver.find_element(By.CSS_SELECTOR, 'button.btn_search').click()
driver.implicitly_wait(100)
time.sleep(1)
driver.find_element(By.CSS_SELECTOR,'a[href="https://pedia.watcha.com/"]').click()
time.sleep(1)

# 탭전환
driver.switch_to.window(driver.window_handles[-1])

"""
Trouble Shooting **Done**
"""
# driver = webdriver.Chrome()
# driver.get(url="https://pedia.watcha.com/ko-KR")
# driver.implicitly_wait(100)

# 로그인
"""
왓챠피디아는 로그인하지 않은 게스트 상태로 리뷰를 볼 수 없으므로 로그인 과정 추가
"""
delete_ad(driver)
driver.find_element(By.CSS_SELECTOR, 'body > main > div:nth-of-type(1) > header:nth-of-type(1) > nav > section > ul > li:nth-child(8) > button').click()
driver.implicitly_wait(100)
driver.find_element(By.CSS_SELECTOR, 'div[data-select="sign-in-dialog"] form > div:nth-of-type(1) > label > div > input').send_keys(USER_ID)
driver.implicitly_wait(100)
driver.find_element(By.CSS_SELECTOR, 'div[data-select="sign-in-dialog"] form > div:nth-of-type(2) > label > div > input').send_keys(USER_PWD+"\n")
time.sleep(1)


# 영화 검색하기
delete_ad(driver)
# body > main > div:nth-of-type(1) > header:nth-of-type(1) > nav > section > ul > li:nth-child(8) input[autocomplete="off"]
search = driver.find_element(By.CSS_SELECTOR, '#desktop-search-field')
search.send_keys(MOVIE_TITLE+"\n")
time.sleep(1)

# 첫 번째 검색결과 클릭하기
driver.find_element(By.CSS_SELECTOR,f'a[title="{MOVIE_TITLE}"]').click()
driver.implicitly_wait(100)

# 더보기 클릭하기
delete_ad(driver)
driver.find_element(By.CSS_SELECTOR,'body > main > div:nth-of-type(1) > section > div > div:nth-of-type(2) > section > section:nth-child(3) > header > div > div > a').click()
driver.implicitly_wait(100)

# 리뷰 작성자 및 내용 추출
"""
reviewers -> 리뷰를 작성한 유저명이 담긴 html 태그를 iterable한 객체(List)로 저장
reviews -> 리뷰의 내용이 담긴 html 태그를 iterable한 객체(List)로 저장
"""
body = driver.find_element(By.CSS_SELECTOR, 'body')
reviews, reviewers, rating = [], [], []
for i in range(COUNT) :
    # body 태그에 END 키를 입력하는 것으로 페이지 최하단으로 스크롤
    body.send_keys(Keys.END)
    # 원활한 페이지 로딩을 위한 멈춤
    time.sleep(2)

# List 새로고침
rating = driver.find_elements(By.CSS_SELECTOR, 'body > main > div > section > div:nth-of-type(2) li:nth-of-type(n) > article > a:nth-of-type(1) > header > div:nth-of-type(2) > p')
reviewers = driver.find_elements(By.CSS_SELECTOR, 'body > main > div > section > div:nth-of-type(2) li:nth-of-type(n) > article > a:nth-of-type(1) > header > div:nth-of-type(1) > p')
reviews = driver.find_elements(By.CSS_SELECTOR, 'body > main > div > section > div:nth-of-type(2) li:nth-of-type(n) > article > a:nth-of-type(2) > p')

# pandas dataframe
data = []
for user, rev, rat in zip(reviewers, reviews, rating):
    data.append({"reviewer": user.text, "review": rev.text.replace("\n"," "), "rating": float(rat.text)})
df = pd.DataFrame(data)

print(df)
print(get_word_frequencies(df["review"], top_n=20))
print(konlpy(df["review"], top_n=20))

df.to_csv("reviews.csv", index=False)

# pause for 10sec, and terminate
time.sleep(10)
driver.quit()