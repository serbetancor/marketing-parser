import json

def calculate_average(numbers):
    if len(numbers) == 0:
        return 0 
    total = sum(numbers)
    average = total / len(numbers)
    return average

with open('../data/productsStradivarius.json', 'r') as jsonFile:
    data = json.load(jsonFile)