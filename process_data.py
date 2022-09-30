import json
import csv

attendances = {}
# Open attendances JSON file
with open('data/attendances.json') as f:
  attendances = json.loads(f.read())

print("processed", len(attendances), "attendances")

# add your code for processing this data here! 
# see https://github.com/mobilizeamerica/api#attendances for data model documentation