import time, re, os, emoji

import pandas as pd

from typing import List, Tuple, NoReturn, Union
from collections import Counter
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

# **Unused** 주석이 붙어 있는 함수의 경우 현재 코드 내에서 사용되지 않음. 중간 발표에 사용된 부분이며 추후 필요시 활용 가능
# konlpy 패키지가 설치되지 않은 경우 해당 주석이 붙은 함수와 import 문을 제거한 뒤 실행해도 무방

# **Unused**
from konlpy.tag import Okt

# **Unused**
def konlpy(strings: List[str], top_n: int = None) -> List[Tuple[str, int]]:
    # koNLPy 를 사용한 빈도수 추출
    """
    여러 문자열 리스트(strings)를 받아 자주 등장하는 단어(빈도순)와 단어별 가중치(등장 횟수)를 반환.
    :param strings: 문자열 리스트
    :param top_n: 등장 횟수 상위 n개만 리턴 (None 인 경우 전체 리턴)
    :return: [(단어, 등장횟수), ...] 형태의 리스트
    """
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


# **Unused**
def get_word_frequencies(strings: List[str], top_n: int = None) -> List[Tuple[str, int]] :
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


def make_csv_path() -> None :
    # watcha_reviews_csv 디렉토리 생성
    cur_path = os.getcwd()
    csv_path = rf"{cur_path}\watcha_reviews_csv"
    if not os.path.exists(csv_path) :
        os.makedirs(csv_path)
        print(f"Directory created: {csv_path}")
    else :
        print(f"Directory already exists: {csv_path}")


def print_current_env() -> None :
    # 현재 환경변수 및 작업 경로 출력
    print("Current Environment Variables :")
    for key, value in os.environ.items() :
        print(f"{key}: {value}")
    print("Current Working Directory : ", os.getcwd(),"\n")


def delete_ad(driver: webdriver.Chrome, action: ActionChains) -> None :
    # 팝업 광고 제거
    """
    팝업 광고 버튼이 화면에 나타난 경우
    해당 버튼을 클릭해 광고 제거
    """
    try :
        driver.implicitly_wait(0.5)
        ad_close_button = driver.find_element(By.CSS_SELECTOR, 'div.WelcomeDisplayModal > div:nth-of-type(2) > button:nth-of-type(2)')
        
        if ad_close_button.is_displayed() :
            action.move_to_element(ad_close_button).click().perform()

    except Exception as e :
        print(f"POP_UP_AD_NOT_FOUND : pop-up ad_close_button not found or cannot interact")
        pass


def initial_setup(driver: webdriver.Chrome, action: ActionChains) -> Union[None, NoReturn] :
    """
    브라우저 초기 설정
    1. 빈 페이지 열기
    2. 창 최대화
    """
    try :
        # 브라우저 초기 설정
        driver.implicitly_wait(3)
        driver.get("about:blank")
        driver.maximize_window()
    except Exception as e :
        print(f"{e} : initial_setup error")
        raise Exception(e)


def watcha_open_page(driver: webdriver.Chrome, action: ActionChains) -> Union[None, NoReturn] :
    """
    왓챠피디아 페이지 열기
    1. 새 탭(왓챠피디아) 열기
    2. 이전 탭 닫기
    3. 새 탭으로 탭 전환
    """
    try :
        # 새 탭 열기(왓챠피디아)
        driver.implicitly_wait(5)
        driver.execute_script("window.open('https://pedia.watcha.com/');")
        

        # 현재 탭(초기 혹은 이전 탭) 닫기
        driver.close()

        # 탭전환(왓챠피디아)
        driver.implicitly_wait(5)
        driver.switch_to.window(driver.window_handles[0])
    except Exception as e:
        print(f"{e} : watcha_open_page invalid or cannot interact")
        raise Exception(e)


def watcha_login(driver: webdriver.Chrome, action: ActionChains, USER_ID: str, USER_PWD: str) -> Union[None, NoReturn] :
    # 로그인
    """
    왓챠피디아 로그인
    1. 로그인 버튼 클릭
    2. 아이디 및 비밀번호 입력(전송)
    """
    delete_ad(driver, action)
    try :
        login_dialog = driver.find_element(By.CSS_SELECTOR, 'body > main > div:nth-of-type(1) > header:nth-of-type(1) > nav > section > ul > li:nth-child(8) > button')
        login_dialog.click()
        
        driver.implicitly_wait(3)
        ID_input = driver.find_element(By.CSS_SELECTOR, 'div[data-select="sign-in-dialog"] form > div:nth-of-type(1) > label > div > input')
        action.move_to_element(ID_input).click().send_keys(USER_ID).perform()
        time.sleep(0.5)

        PWD_input = driver.find_element(By.CSS_SELECTOR, 'div[data-select="sign-in-dialog"] form > div:nth-of-type(2) > label > div > input')
        action.move_to_element(PWD_input).click().send_keys(USER_PWD).perform()
        time.sleep(0.5)
        
        login_button = driver.find_element(By.CSS_SELECTOR, 'div[data-select="sign-in-dialog"] form > button')
        action.move_to_element(login_button).click().perform()
        time.sleep(2)

    except Exception as e :
        print(f"{e} : watcha_login element not found or cannot interact")
        raise Exception(e)
    

def watcha_search_movie(driver: webdriver.Chrome, action: ActionChains, title: str) -> Union[str, NoReturn] :
    # 영화 검색하기
    """
    영화 검색하기
    1. 검색창에 영화 제목 입력(전송)
    2. 검색 결과에서 해당 영화 클릭

    :return: 영화 연도 (str)
    """
    delete_ad(driver, action)
    try :
        # body > main > div:nth-of-type(1) > header:nth-of-type(1) > nav > section > ul > li:nth-child(8) input[autocomplete="off"]
        driver.implicitly_wait(3)
        search = driver.find_element(By.CSS_SELECTOR, '#desktop-search-field')
        action.move_to_element(search).click().send_keys(title+"\n").perform()

        # 영화 연도 추출
        # body > main > div:nth-of-type(1) > section > section > div.nth-of-type(2) > div:nth-child(1) > section > section.nth-of-type(2) > div.nth-of-child(1) > ul > li > a > div.nth-of-type(2) > div.nth-of-type(2)
        driver.implicitly_wait(3)
        year_info = driver.find_element(By.CSS_SELECTOR,f'a[title="{MOVIE_TITLE}"] > div:nth-of-type(2) > div:nth-of-type(2)').text
        YEAR = re.findall(r'\d{4}', year_info)[0]

        # 첫 번째 검색결과 클릭하기
        # body > main > div:nth-of-type(1) > section > section > div:nth-of-type(2) > div:nth-child(1) > section > section:nth-of-type(2) > div:nth-of-child(1) > ul > li:nth-child(1) > a
        driver.implicitly_wait(3)
        movie_page = driver.find_element(By.CSS_SELECTOR,f'a[title="{title}"]')
        action.move_to_element(movie_page).click().perform()

        return YEAR
    except Exception as e :
        print(f"{e} : watcha_search_movie element not found or cannot interact")
        raise Exception(e)


def watcha_open_reviews(driver: webdriver.Chrome, action: ActionChains) -> Union[None, NoReturn] :
    # 더보기 클릭하기
    delete_ad(driver, action)
    try :
        time.sleep(0.5)
        driver.implicitly_wait(3)
        review_drawer = driver.find_element(By.CSS_SELECTOR,'body > main > div:nth-of-type(1) > section > div > div:nth-of-type(2) > section > section:nth-child(3) > header > div > div > a')
        action.move_to_element(review_drawer).click().perform()
    except Exception as e:
        print(f"{e} : watcha_open_reviews element not found or cannot interact")
        raise Exception(e)


def watcha_load_reviews(driver: webdriver.Chrome, action: ActionChains) -> Union[None, NoReturn] :
    # 동적 페이지 로드 (스크롤 다운)
    try :
        body = driver.find_element(By.CSS_SELECTOR, 'body')

        # 화면 스크롤 횟수 (150회 설정 시 약 2600개 리뷰 로드, 100회 때 페이지 메모리 1.1GB 정도 썼는데 150회는 모르겠고 꽤 많이 사용)
        COUNT = 155
        
        for i in tqdm(range(COUNT), desc=f"Loading Reviews : {MOVIE_TITLE}", mininterval=1, total=COUNT) :
            # body 태그에 END 키를 입력하는 것으로 페이지 최하단으로 스크롤
            body.send_keys(Keys.END)
            # 원활한 페이지 로딩을 위한 멈춤
            time.sleep(0.7)

    except Exception as e:
        print(f"{e} : watcha_load_reviews element not found or cannot interact")
        raise Exception(e)


def watcha_extract_reviews(driver: webdriver.Chrome, action: ActionChains) -> Union[pd.DataFrame, NoReturn] :
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


def watcha_spoiler_reveal(driver: webdriver.Chrome, action: ActionChains) -> Union[None, NoReturn] :
    # 스포일러 리뷰 보기 클릭
    """
    스포일러 리뷰가 있는 경우
    1. 스포일러 보기 버튼을 모두 검색
    2. 각 버튼의 위치로 이동한 뒤 클릭 수행
    """
    try :
        spoiler_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[class*="acceptSpoiler"]')
        # 클릭한 스포일러 버튼 개수 **FOR DEBUGGING**
        # iter = 1
        for button in tqdm(spoiler_buttons, desc=f"Revealing Spoiler Reviews : {MOVIE_TITLE}", mininterval=1, total=len(spoiler_buttons)) :
            if button.is_enabled() :
                action.move_to_element(button).click().perform()
                driver.implicitly_wait(100)
                # 클릭한 스포일러 버튼 기록 **FOR DEBUGGING**
                # print(f"Spoiler button #{iter} clicked")
                # iter += 1
    except Exception as e :
        print(f"{e} : Spoiler buttons not found or incorrect selector")
        raise Exception(e)


def df_filter_spoiler_reviews(df: pd.DataFrame) -> Union[None, NoReturn] :
    # 리뷰 DataFrame에서 스포일러방지 리뷰 필터링
    # watcha_spoiler_reveal() 이후 남아있을 수 있는 스포일러방지 리뷰 필터링
    """
    인자로 받은 DataFrame 내에서 'review' col의 값이
    "스포일러가 있어요!!보기" 인 row를 찾아 삭제.

    df.drop() method의 parameter inplace가 True로 설정되어 있어
    함수의 인자로 전달받은 df의 원본이 수정됨.

    df의 원본을 유지하고 싶은 경우 df.drop() method의 parameter inplace를 False로 변경하고
    try 문 내 return df 코드를 활성화. 자세한 사항은 해당 코드 내 주석 참고.
    """
    try :
        spoiler_df = df[df['review'] == "스포일러가 있어요!!보기"]

        if spoiler_df.empty :
            print(f"No spoiler reviews remaining in {MOVIE_TITLE_EN} reviews.")
            return
        else :
            print(f"Deleting spoiler reviews remaining in {MOVIE_TITLE_EN} reviews, count: {len(spoiler_df)}")
            # 스포일러방지 리뷰 삭제 후 DataFrame 반환 (inplace=False 로 변경시 원본 DataFrame 유지 & df를 함수에서 반환 해주어야함.)
            df.drop(spoiler_df.index, inplace=True)
            # inplace=False 로 변경 시 해당 리턴 코드 사용 및 type hint 변경 필요
            # return df
    except Exception as e :
        print(f"{e} : df_filter_spoiler_reviews index not found or cannot delete")
        raise Exception(e)


if __name__ == "__main__" :
    # 왓챠피디아 아이디
    USER_ID = "lgr9603@kangwon.ac.kr"
    USER_PWD = "lgr2618409!"

    # 검색할 영화명
    """
    ** 주의점 **
    영화명을 검색한 뒤 제목이 완전히 동일한 영화를 크롤링하므로 영화 제목에 오탈자가 완전히 없어야 함.(띄어쓰기 포함)
    ex. "오징어게임" vs "오징어 게임 시즌 1"  **띄어쓰기 및 시즌 주의**
    """
    # e.g.
    # MOVIE_TITLE = "폭싹 속았수다"
    # MOVIE_TITLE_EN = "When Life Gives You Tangerines"

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

    # Selenium WebDriver 및 ActionChains 객체 생성
    # **CAUTION** webdriver를 인자로 받는 모든 함수는 ActionChains 객체를 함께 인자로 받음
    driver = webdriver.Chrome()
    action = ActionChains(driver)

    # 리뷰 저장 디렉토리 
    print("\nCSV Directory Setup :")
    make_csv_path()

    # 브라우저 초기 설정
    initial_setup(driver, action)

    watcha_open_page(driver, action)

    watcha_login(driver, action, USER_ID, USER_PWD)

    # 영화제목 리스트를 순회하며 크롤링
    # **CAUTION** MOVIE_TITLE_LIST, MOVIE_TITLE_EN_LIST 영화 제목의 순서가 동일해야함
    for MOVIE_TITLE, MOVIE_TITLE_EN in zip(MOVIE_TITLE_LIST, MOVIE_TITLE_EN_LIST) :
        # 각 영화별 크롤링 try-except 문
        # try 문 내 어떠한 함수에서 예외가 발생한 경우 해당 영화 크롤링을 건너뛰고 에러가 발생한 함수명을 출력함
        try :
            print()
            print(f"Start Crawling : {MOVIE_TITLE_EN}")

            watcha_open_page(driver, action)

            MOVIE_YEAR = watcha_search_movie(driver, action, MOVIE_TITLE)

            watcha_open_reviews(driver, action)

            watcha_load_reviews(driver, action)

            watcha_spoiler_reveal(driver, action)

            time.sleep(1)

            df = watcha_extract_reviews(driver, action)

            # DataFrame preview 출력 **FOR MID-TERM PRESENTATION**
            # print(df)
            # print(get_word_frequencies(df["review"], top_n=20))
            # print(konlpy(df["review"], top_n=20))

            # df 원본을 modify 하도록 구현, 원본을 유지하고 싶은 경우 함수 내 주석 참고
            df_filter_spoiler_reviews(df)

            # 크롤링 결과 CSV 파일로 저장
            MOVIE_TITLE_CSV = re.sub(r'[^a-zA-Z0-9가-힣.]', '', MOVIE_TITLE_EN)
            df.to_csv(f"./watcha_reviews_csv/watcha_korean_{MOVIE_TITLE_CSV}_reviews_minimal.csv", index=False)

        except Exception as e:
            print(f"Error processing movie {MOVIE_TITLE_EN} : {e}")
            continue

    # 종료 전 5초간 대기 및 브라우저 종료
    print("Crawling completed. Code execution will finish after this message.")
    time.sleep(5)
    driver.quit()

#TODO: 영화 제목을 리스트로 구성, 현재 main 부분을 함수화하여 for문으로 여러 영화 크롤링 가능하게 하기 **DONE**
#TODO: CSS Selector 예외처리 및 각 선택자 변수지정 **DONE**
#TODO: 리뷰 내용 중 비언어적 문자(ex: emoji) 삭제 **DONE**
#TODO: 리뷰 내용의 길이에 따라 필터링 기능 추가하기 
#TODO: 리뷰에 스포일러 방지가 있는 경우 텍스트가 표시되지 않음. 이 경우 스포일러 방지 해제 **DONE** 크롤링에서 제외하기 **DONE**
#TODO: 영화별로 크롤링 결과를 다른 파일에 저장하고, 각 파일명에 영화 제목 포함시키기 **DONE**
#TODO: 가능하다면 리뷰 작성 일자도 크롤링하기 