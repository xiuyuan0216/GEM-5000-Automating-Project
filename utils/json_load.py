import json 

# load json files in json folder into python dictionaries

with open("./json/limit_bound.json",'r') as file1:
    limit_bound = json.load(file1)

with open("./json/mapping.json",'r') as file2:
    mapping = json.load(file2)

with open("./json/slope_bound.json","r") as file3:
    slope_bound = json.load(file3)

with open('./json/error_message.json','r') as file4:
    error_message = json.load(file4)

with open('./json/error_reason.json','r') as file5:
    error_reason = json.load(file5)