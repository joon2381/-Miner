import os

# 이 코드는 현재 환경변수와 작업 중인 경로를 출력합니다.
# 주로 디버깅, 환경 확인 등에 사용됩니다.

print("Current Environment Variables :")
for key, value in os.environ.items() :
    print(f"{key}: {value}")
print("Current Working Directory : ", os.getcwd())