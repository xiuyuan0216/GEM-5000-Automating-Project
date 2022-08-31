import json 

with open("./json/limit_bound.json",'r') as file1:
    limit_bound = json.load(file1)

with open("./json/mapping.json",'r') as file2:
    mapping = json.load(file2)

with open("./json/slope_bound.json","r") as file3:
    slope_bound = json.load(file3)