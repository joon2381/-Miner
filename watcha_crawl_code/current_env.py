import os

# 해당 코드는 현재 작업 환경을 설정하고 watcha_review_csv 디렉토리를 생성하는 기능을 테스트 하는 데에 사용된 코드입니다.
# 동일한 기능이 watcha_reviews_crawl.py 파일 내에도 독립된 함수로 존재합니다.

# 디렉토리 생성 함수
def make_csv_path() -> None :
    cur_path = os.getcwd()
    if not os.path.exists(f"{cur_path}/watcha_reviews_csv") :
        os.makedirs(f"{cur_path}/watcha_reviews_csv")
    else :
        print(f"Directory already exists: {cur_path}/watcha_reviews_csv")

# 현재 환경변수 및 작업 경로 출력 함수
def print_current_env() -> None :
    print("Current Environment Variables :")
    for key, value in os.environ.items() :
        print(f"{key}: {value}")
    print("Current Working Directory : ", os.getcwd(),"\n")

print_current_env()
make_csv_path()