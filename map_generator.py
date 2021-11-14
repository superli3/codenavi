import pandas as pd
import os
import json
import re

#set source_folder to location of PR committed files
source_folder = 'D:\\MIDS\\CYRMPR\\raw_json_Closed_PR_files'
files = os.listdir(source_folder)
files = [item for item in files if item.startswith('Closed_PRs_')]

parsed_files_folder = 'D:\\mids\\real_parsed_data'
directories =[os.path.join(parsed_files_folder, o).rsplit('\\')[-1] for o in os.listdir(parsed_files_folder) 
                    if os.path.isdir(os.path.join(parsed_files_folder,o))]


labels = pd.read_csv('D:\\mids\\ai_bug_detector\\labeled_bugs.csv').fillna(0)
labels['PR_Number'] = labels['PR_Number'].astype(int)

mapping = pd.DataFrame()

for file in files:
    full_file_path = source_folder + '\\' + file
    pr_number = int(re.findall(r'\d+', file)[0])
    print(full_file_path)
    with open(full_file_path) as jsonfile:
        PRs = json.load(jsonfile)
        for PR in PRs:
            try:
                mapping = mapping.append(pd.DataFrame({'PR_Number': [PR['number']], 'sha': [PR['_links']['statuses']['href'].rsplit('/')[-1]]}))
            except:
                continue


mapping = mapping.reset_index()

#confirm dest folder matches with hashes
overlap = list(set(mapping['sha'].to_list()) & set(directories))
print(len(overlap))

joined_data = pd.merge(mapping,labels, on='PR_Number', how='left')
joined_data['Label'] = joined_data['Issue ID'].apply(lambda x: "Negative" if pd.isnull(x) else "Positive")

joined_data.to_csv('mapping.csv', index=False)