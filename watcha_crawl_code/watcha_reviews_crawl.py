import time, re

import pandas as pd

from collections import Counter
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from konlpy.tag import Okt


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
def get_word_frequencies(strings: list[str], top_n: int = None) -> list[tuple[str, int]]:
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
def delete_ad(driver: webdriver.Chrome) -> None :
    try :
        ad_close_button = driver.find_element(By.CSS_SELECTOR, 'div.WelcomeDisplayModal > div:nth-of-type(2) > button:nth-of-type(2)')
        
        if ad_close_button.is_displayed() :
            ad_close_button.click()

        driver.implicitly_wait(100)
    except Exception as e :
        print(f"{e} : pop-up ad_close_button not found or cannot interact")
        pass

def watcha_open_page(driver: webdriver.Chrome) -> None :
    # 크롬 드라이버로 네이버 열기
    URL = 'https://naver.com'
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

def watcha_login(driver: webdriver.Chrome, USER_ID: str, USER_PWD: str) -> None :
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

def watcha_search_movie(driver: webdriver.Chrome, title: str) -> str :
    # 영화 검색하기
    delete_ad(driver)
    # body > main > div:nth-of-type(1) > header:nth-of-type(1) > nav > section > ul > li:nth-child(8) input[autocomplete="off"]
    search = driver.find_element(By.CSS_SELECTOR, '#desktop-search-field')
    search.send_keys(title+"\n")
    time.sleep(1)

    # 영화 연도 추출
    # body > main > div:nth-of-type(1) > section > section > div.nth-of-type(2) > div:nth-child(1) > section > section.nth-of-type(2) > div.nth-of-child(1) > ul > li > a > div.nth-of-type(2) > div.nth-of-type(2)
    year_info = driver.find_element(By.CSS_SELECTOR,f'a[title="{MOVIE_TITLE}"] > div:nth-of-type(2) > div:nth-of-type(2)').text
    YEAR = re.findall(r'\d{4}', year_info)[0]

    # 첫 번째 검색결과 클릭하기
    driver.find_element(By.CSS_SELECTOR,f'a[title="{title}"]').click()
    driver.implicitly_wait(100)

    return YEAR

def watcha_open_reviews(driver: webdriver.Chrome) -> None :
    # 더보기 클릭하기
    delete_ad(driver)
    driver.find_element(By.CSS_SELECTOR,'body > main > div:nth-of-type(1) > section > div > div:nth-of-type(2) > section > section:nth-child(3) > header > div > div > a').click()
    driver.implicitly_wait(100)

def watcha_load_reviews(driver: webdriver.Chrome) -> None :
    body = driver.find_element(By.CSS_SELECTOR, 'body')

    # 화면 스크롤 횟수 (100회 설정 시 약 1750개 리뷰 로드, 페이지 메모리 1.1GB 정도 사용)
    COUNT = 100

    for i in range(COUNT) :
        # body 태그에 END 키를 입력하는 것으로 페이지 최하단으로 스크롤
        body.send_keys(Keys.END)
        # 원활한 페이지 로딩을 위한 멈춤
        time.sleep(0.5)

def watcha_extract_reviews(driver: webdriver.Chrome) -> pd.DataFrame :
    # 리뷰 작성자 및 내용 추출
    """
    reviewers -> 리뷰를 작성한 유저명이 담긴 html 태그를 iterable한 객체(List)로 저장
    reviews -> 리뷰의 내용이 담긴 html 태그를 iterable한 객체(List)로 저장
    """
    reviews, reviewers, rating = [], [], []

    # List 새로고침
    rating = driver.find_elements(By.CSS_SELECTOR, 'body > main > div > section > div:nth-of-type(2) li:nth-of-type(n) > article > a:nth-of-type(1) > header > div:nth-of-type(2) > p')
    reviewers = driver.find_elements(By.CSS_SELECTOR, 'body > main > div > section > div:nth-of-type(2) li:nth-of-type(n) > article > a:nth-of-type(1) > header > div:nth-of-type(1) > p')
    reviews = driver.find_elements(By.CSS_SELECTOR, 'body > main > div > section > div:nth-of-type(2) li:nth-of-type(n) > article > a:nth-of-type(2) > p')

    # pandas dataframe
    data = []
    for user, rev, rat in tqdm(zip(reviewers, reviews, rating), desc="Constructing DataFrame", mininterval=1):
        username = user.text
        review_text = rev.text.replace("\n"," ")
        review_len = len(review_text)
        rating_value = float(rat.text)
        data.append({"site": "watcha", "title": MOVIE_TITLE, "title_en": MOVIE_TITLE_EN, "year": MOVIE_YEAR, "reviewer": username, "review": review_text, "review_length": review_len, "rating": rating_value})
    df = pd.DataFrame(data)

    return df


driver = webdriver.Chrome()

watcha_open_page(driver)

# 왓챠피디아 아이디
USER_ID = "lgr9603@kangwon.ac.kr"
USER_PWD = "lgr2618409!"

watcha_login(driver, USER_ID, USER_PWD)

# 검색할 영화명
"""
** 주의점 **
영화명을 검색한 뒤 가장 처음 검색 결과로 나온 영화의 리뷰를 크롤링하므로 영화 제목의 오탈자에 주의할 것
"""
MOVIE_TITLE = "폭싹 속았수다"
MOVIE_TITLE_EN = "When Life Gives You Tangerines"

MOVIE_YEAR = watcha_search_movie(driver, MOVIE_TITLE)

watcha_open_reviews(driver)

watcha_load_reviews(driver)

df = watcha_extract_reviews(driver)

print(df)
print(get_word_frequencies(df["review"], top_n=20))
print(konlpy(df["review"], top_n=20))

df.to_csv("watcha_korean_reviews_minimal.csv", index=False)

# Wait for user input for termination
input("Press Enter to terminate...")
driver.quit()

#TODO: 영화 제목을 리스트로 구성, 현재 main 부분을 함수화하여 for문으로 여러 영화 크롤링 가능하게 하기
#TODO: 리뷰 내용 중 비언어적 문자(ex: emoji) 삭제 및 리뷰 내용의 길이에 따라 필터링 기능 추가하기
#TODO: 영화별로 크롤링 결과를 다른 파일에 저장하고, 각 파일명에 영화 제목 포함시키기
#TODO: 가능하다면 리뷰 작성 일자도 크롤링하기