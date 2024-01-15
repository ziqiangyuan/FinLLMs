import json
with open('data/all_function.json','r', encoding='utf-8') as file:
    file_test = json.load(file)
print(len(file_test))