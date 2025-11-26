import time, re

import pandas as pd

from collections import Counter
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import emoji

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


def get_word_frequencies(strings: list[str], top_n: int = None) -> list[tuple[str, int]] :
    # 단어별 빈도수 추출
    """
    여러 문자열 리스트(strings)를 받아 자주 등장하는 단어(빈도순)와 단어별 가중치(등장 횟수)를 반환합니다.
    """
    words = []
    for s in strings:
        # 소문자로 변환 후, 단어만 추출 (영어 기준, 한글은 \w에 포함)
        words += re.findall(r'\w+', s.lower())
    counter = Counter(words)
    if top_n:
        return counter.most_common(top_n)
    else:
        return counter.most_common()


def delete_ad(driver: webdriver.Chrome) -> None :
    # 팝업 광고 제거
    """
    팝업 광고 버튼이 화면에 나타난 경우
    해당 버튼을 클릭해 광고 제거
    """
    try :
        ad_close_button = driver.find_element(By.CSS_SELECTOR, 'div.WelcomeDisplayModal > div:nth-of-type(2) > button:nth-of-type(2)')
        
        if ad_close_button.is_displayed() :
            ad_close_button.click()

        driver.implicitly_wait(100)
    except Exception as e :
        print(f"{e} : pop-up ad_close_button not found or cannot interact")
        raise Exception(e)

def initial_setup(driver: webdriver.Chrome) -> None :
    """
    브라우저 초기 설정
    1. 빈 페이지 열기
    2. 창 최대화
    """
    try :
        # 브라우저 초기 설정
        driver.get("about:blank")
        driver.maximize_window()
        driver.implicitly_wait(100)
    except Exception as e :
        print(f"{e} : initial_setup error")
        raise Exception(e)

def watcha_open_page(driver: webdriver.Chrome) -> None :
    """
    왓챠피디아 페이지 열기
    1. 새 탭(왓챠피디아) 열기
    2. 이전 탭 닫기
    3. 새 탭으로 탭 전환
    """
    try :
        # 새 탭 열기(왓챠피디아)
        driver.execute_script("window.open('https://pedia.watcha.com/');")
        driver.implicitly_wait(100)

        # 현재 탭(초기 혹은 이전 탭) 닫기
        driver.close()
        driver.implicitly_wait(100)

        # 탭전환(왓챠피디아)
        driver.switch_to.window(driver.window_handles[0])
    except Exception as e:
        print(f"{e} : watcha_open_page invalid or cannot interact")
        raise Exception(e)

def watcha_login(driver: webdriver.Chrome, USER_ID: str, USER_PWD: str) -> None :
    # 로그인
    """
    왓챠피디아 로그인
    1. 로그인 버튼 클릭
    2. 아이디 및 비밀번호 입력(전송)
    """
    delete_ad(driver)
    try :
        login_button = driver.find_element(By.CSS_SELECTOR, 'body > main > div:nth-of-type(1) > header:nth-of-type(1) > nav > section > ul > li:nth-child(8) > button')
        login_button.click()
        driver.implicitly_wait(100)
        
        ID_input = driver.find_element(By.CSS_SELECTOR, 'div[data-select="sign-in-dialog"] form > div:nth-of-type(1) > label > div > input')
        ID_input.send_keys(USER_ID)
        driver.implicitly_wait(100)

        PWD_input = driver.find_element(By.CSS_SELECTOR, 'div[data-select="sign-in-dialog"] form > div:nth-of-type(2) > label > div > input')
        PWD_input.send_keys(USER_PWD+"\n")
        time.sleep(1)
    except Exception as e :
        print(f"{e} : watcha_login element not found or cannot interact")
        raise Exception(e)
    

def watcha_search_movie(driver: webdriver.Chrome, title: str) -> str|None :
    # 영화 검색하기
    """
    영화 검색하기
    1. 검색창에 영화 제목 입력(전송)
    2. 검색 결과에서 해당 영화 클릭

    :return: 영화 연도 (str)
    """
    delete_ad(driver)
    try :
        # body > main > div:nth-of-type(1) > header:nth-of-type(1) > nav > section > ul > li:nth-child(8) input[autocomplete="off"]
        search = driver.find_element(By.CSS_SELECTOR, '#desktop-search-field')
        search.send_keys(title+"\n")
        time.sleep(1)

        # 영화 연도 추출
        # body > main > div:nth-of-type(1) > section > section > div.nth-of-type(2) > div:nth-child(1) > section > section.nth-of-type(2) > div.nth-of-child(1) > ul > li > a > div.nth-of-type(2) > div.nth-of-type(2)
        year_info = driver.find_element(By.CSS_SELECTOR,f'a[title="{MOVIE_TITLE}"] > div:nth-of-type(2) > div:nth-of-type(2)').text
        YEAR = re.findall(r'\d{4}', year_info)[0]

        # 첫 번째 검색결과 클릭하기
        # body > main > div:nth-of-type(1) > section > section > div:nth-of-type(2) > div:nth-child(1) > section > section:nth-of-type(2) > div:nth-of-child(1) > ul > li:nth-child(1) > a
        movie_page = driver.find_element(By.CSS_SELECTOR,f'a[title="{title}"]')
        movie_page.click()
        driver.implicitly_wait(100)

        return YEAR
    except Exception as e :
        print(f"{e} : watcha_search_movie element not found or cannot interact")
        raise Exception(e)


def watcha_open_reviews(driver: webdriver.Chrome) -> None :
    # 더보기 클릭하기
    delete_ad(driver)
    try :
        review_drawer = driver.find_element(By.CSS_SELECTOR,'body > main > div:nth-of-type(1) > section > div > div:nth-of-type(2) > section > section:nth-child(3) > header > div > div > a')
        review_drawer.click()
        driver.implicitly_wait(100)
    except Exception as e:
        print(f"{e} : watcha_open_reviews element not found or cannot interact")
        raise Exception(e)

def watcha_load_reviews(driver: webdriver.Chrome) -> None :
    try :
        body = driver.find_element(By.CSS_SELECTOR, 'body')

        # 화면 스크롤 횟수 (100회 설정 시 약 1750개 리뷰 로드, 페이지 메모리 1.1GB 정도 사용)
        COUNT = 150
        
        for i in tqdm(range(COUNT), desc=f"Loading Reviews : {MOVIE_TITLE}", mininterval=1, total=COUNT) :
            # body 태그에 END 키를 입력하는 것으로 페이지 최하단으로 스크롤
            body.send_keys(Keys.END)
            # 원활한 페이지 로딩을 위한 멈춤
            time.sleep(0.5)

    except Exception as e:
        print(f"{e} : watcha_load_reviews element not found or cannot interact")
        raise Exception(e)

def watcha_extract_reviews(driver: webdriver.Chrome) -> pd.DataFrame|None :
    # 리뷰 작성자 및 내용 추출
    """
    rating -> 리뷰에 대한 평점이 담긴 html 태그를 iterable한 객체(List)로 저장
    reviewers -> 리뷰를 작성한 유저명이 담긴 html 태그를 iterable한 객체(List)로 저장
    reviews -> 리뷰의 내용이 담긴 html 태그를 iterable한 객체(List)로 저장

    이후 각 정보를 pandas DataFrame 형태로 변환(merge)하여 return
    """
    reviews, reviewers, rating = [], [], []
    try :
        # List 새로고침
        rating = driver.find_elements(By.CSS_SELECTOR, 'body > main > div > section > div:nth-of-type(2) li:nth-of-type(n) > article > a:nth-of-type(1) > header > div:nth-of-type(2) > p')
        reviewers = driver.find_elements(By.CSS_SELECTOR, 'body > main > div > section > div:nth-of-type(2) li:nth-of-type(n) > article > a:nth-of-type(1) > header > div:nth-of-type(1) > p')
        reviews = driver.find_elements(By.CSS_SELECTOR, 'body > main > div > section > div:nth-of-type(2) li:nth-of-type(n) > article > a:nth-of-type(2) > p')
        
        # 스포일러 리뷰 보기 클릭 **현재 작동 안 됨 - IN-PROGRESS**
        # for iter in tqdm(range(len(reviews)), desc=f"Unveiling Spoiler Reviews : {MOVIE_TITLE}:", mininterval=1, total=len(reviews)) :
        #     try :
        #         spoiler_button = driver.find_element(By.CSS_SELECTOR, f'body > main > div > section > div:nth-of-type(2) > ul > li:nth-of-type({iter+1}) > article > a:nth-of-type(2) > p > button')
        #         if spoiler_button.is_displayed() :
        #             spoiler_button.click()
        #             driver.implicitly_wait(100)
        #             print(f"Spoiler button clicked for review #{iter+1}")
        #     except Exception as e :
        #         print(f"{e} : Spoiler buttons not found or incorrect selector")
        #         pass

        # pandas dataframe
        data = []
        for user, rev, rat in tqdm(zip(reviewers, reviews, rating), desc=f"Constructing DataFrame : {MOVIE_TITLE}", mininterval=1, total=len(reviews)) :
            username = user.text
            review_text = emoji.replace_emoji(rev.text, replace="").replace("\n"," ")
            review_len = len(review_text)
            rating_value = float(rat.text)
            data.append({"site": "watcha", "title": MOVIE_TITLE, "title_en": MOVIE_TITLE_EN, "year": MOVIE_YEAR, "reviewer": username, "review": review_text, "review_length": review_len, "rating": rating_value})
        df = pd.DataFrame(data)

        return df
    except Exception as e:
        print(f"{e} : watcha_extract_reviews element not found or cannot interact")
        raise Exception(e)

# 왓챠피디아 아이디
USER_ID = "lgr9603@kangwon.ac.kr"
USER_PWD = "lgr2618409!"

# 검색할 영화명
"""
** 주의점 **
영화명을 검색한 뒤 제목이 완전히 동일한 영화를 크롤링하므로 영화 제목에 오탈자가 완전히 없어야 함.(띄어쓰기 포함)
ex) "오징어게임" vs "오징어 게임 시즌 1"  **띄어쓰기 및 시즌 주의**
"""
# e.g.
# MOVIE_TITLE = "폭싹 속았수다"
# MOVIE_TITLE_EN = "When Life Gives You Tangerines"

MOVIE_TITLE_LIST = ["폭싹 속았수다", "오징어 게임 시즌 1"]
MOVIE_TITLE_EN_LIST = ["When Life Gives You Tangerines", "Squid Game Season 1"]

driver = webdriver.Chrome()

# 브라우저 초기 설정
initial_setup(driver)

watcha_open_page(driver)

watcha_login(driver, USER_ID, USER_PWD)

for MOVIE_TITLE, MOVIE_TITLE_EN in zip(MOVIE_TITLE_LIST, MOVIE_TITLE_EN_LIST) :
    try :
        watcha_open_page(driver)

        MOVIE_YEAR = watcha_search_movie(driver, MOVIE_TITLE)

        watcha_open_reviews(driver)

        watcha_load_reviews(driver)

        df = watcha_extract_reviews(driver)

        # print DataFrame preview **FOR MID-TERM PRESENTATION**
        # print(df)
        # print(get_word_frequencies(df["review"], top_n=20))
        # print(konlpy(df["review"], top_n=20))

        df.to_csv(f"./watcha_reviews_csv/watcha_korean_{MOVIE_TITLE_EN.replace(' ', '')}_reviews_minimal.csv", index=False)

    except Exception as e:
        print(f"Error processing movie {MOVIE_TITLE_EN} : {e}")
        continue

# Wait for user input to terminate
input("Press Enter to terminate...")
driver.quit()

#TODO: 영화 제목을 리스트로 구성, 현재 main 부분을 함수화하여 for문으로 여러 영화 크롤링 가능하게 하기 **DONE**
#TODO: CSS Selector 예외처리 및 각 선택자 변수지정 **DONE**
#TODO: 리뷰 내용 중 비언어적 문자(ex: emoji) 삭제 **DONE**
#TODO: 리뷰 내용의 길이에 따라 필터링 기능 추가하기 
#TODO: 리뷰에 스포일러 방지가 있는 경우 텍스트가 표시되지 않음. 이 경우 스포일러 방지 해제 또는 크롤링에서 제외하기 **IN-PROGRESS**
#TODO: 영화별로 크롤링 결과를 다른 파일에 저장하고, 각 파일명에 영화 제목 포함시키기 **DONE**
#TODO: 가능하다면 리뷰 작성 일자도 크롤링하기