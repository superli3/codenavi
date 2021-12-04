import json
import glob
import pandas as pd
import ast
import requests
from os.path import exists
from time import sleep

"""
usage

python mapper.py <github-PAT-api-token>

This script was written with an api rate limiting of 5000/hour
"""

api_token = sys.argv[1]
file_list = glob.glob("D:\\MIDS\\codenavi\\Closed_PRs_*")

print(len(file_list)) 

file = pd.DataFrame()
for i in file_list:
    temp = pd.read_json(i)
    file = file.append(temp)

file = file.reset_index()


def splitter_PR(str):
    return str.rsplit('/', 1)[1]

def prhash(json):
    return json['commits']['href']

file['PRID'] = file['url'].apply(splitter_PR)

commit_urls = file['PRID'].to_list()
commit_urls.sort(reverse=True)

headers = {'Authorization': 'token %s' % api_token}

total_payload = None


for k, v in enumerate(commit_urls):
    url_endpoint = f'https://api.github.com/repos/matplotlib/matplotlib/pulls/{v}/commits'
    if not exists('PRCommits_map_'+ str(v) + '.json'):
        r = requests.get(url_endpoint, headers=headers)
        if r.status_code == 200 and not exists('PRCommits_map_'+ str(v) + '.json'):
            print(v)
            with open('PRCommits_map_'+ str(v) + '.json', 'a') as f:
                json.dump(r.json(), f)
            sleep(1)
        else:
            print(f'stopped due to bad response on value {v}. Exiting now')
            break
    else:
        print(f'skipping {v}, already pulled')
        pass
