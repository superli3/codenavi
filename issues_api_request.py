import requests
import json
import sys
from time import sleep

"""
usage

python api_request.py <github-PAT-api-token>
"""


#items per request
items_per_request = 30

#number of closed PRs
closed_items = 12873

#url endpoint - I have picked out matplot lib
url_endpoint = "https://api.github.com/repos/matplotlib/matplotlib/issues?state=closed"


api_token = sys.argv[1]
headers = {'Authorization': 'token %s' % api_token}


total_payload = None

for i in range(1,650):
    print(i)
    if i == 1:
        r = requests.get(url_endpoint, headers = headers)
    else:
        r = requests.get(url_endpoint + "&page=" + str(i), headers=headers)
    #if total_payload is None:
    #    total_payload = r.json()
    #else:
    ##    total_payload = total_payload + r.json()
    print(r)
    with open('issues_api_request_'+ str(i) + '.json', 'a') as f:
        json.dump(r.json(), f)
    sleep(5)


#print(len(total_payload))

# with open('Closed_PRs.json', 'a') as f:
#     json.dump(r.json(), f)