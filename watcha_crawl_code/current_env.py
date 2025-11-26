# This code is to check the current environment settings(variables, working dir, etc.)
import os

print("Current Environment Variables :")
for key, value in os.environ.items() :
    print(f"{key}: {value}")
print("Current Working Directory : ", os.getcwd())