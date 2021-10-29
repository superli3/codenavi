import json
  
# Opening JSON file
#f = open('Closed_PRs.json',)


with open('Closed_PRs_1.json', 'r') as f2:
    data = f2.read()
#print(f.read())
#lines = f.readlines()
#lines = lines[:-1]
#print(type(f))
# returns JSON object as 
# a dictionary

print(len(data))
data = json.loads(data)
print(len(data))