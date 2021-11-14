import os
import glob
import json

positive_folder = 'D:\\mids\\data\\stage\\positive'
positive_end_file = 'parsed_positive.json'
negative_folder = 'D:\\mids\\data\\stage\\negative'
negative_end_file = 'parsed_negative.json'
ingest = 'D:\\mids\\data\\stage\\ingest_test'
ingest_end_file = 'parsed.json'
#create endpoints if they don't exist
def touch(fname):
    open(fname, 'a').close()
    os.utime(fname, None)

touch(positive_folder + '\\' + positive_end_file)
touch(negative_folder + '\\' + negative_end_file)


result_positive = []

folders = glob.glob(positive_folder + '\\*')
for folder in folders[0:5]:
    subfiles = glob.glob(folder+'\\*')
    for file in subfiles:
        if os.path.getsize(file) > 300 and file[-5:] == '.json':
            with open(file, 'r') as infile:
                record = json.load(infile)
                record['files'][0]['label'] = 'Positive'
                result_positive.append(record)

print(len(result_positive))
#with open(positive_folder + '\\' + positive_end_file, 'w') as outfile:
with open(ingest + '\\' + positive_end_file, 'w') as outfile:
    for i in result_positive:
        json.dump(i, outfile)
        outfile.write('\n')


result_negative = []

folders = glob.glob(negative_folder + '\\*')
for folder in folders[0:5]:
    subfiles = glob.glob(folder+'\\*')
    for file in subfiles:
        if os.path.getsize(file) > 300 and file[-5:] == '.json':
            with open(file, 'r') as infile:
                record['files'][0]['label'] = 'Negative'
                result_negative.append(record)

print(len(result_negative))
#with open(negative_folder + '\\' + negative_end_file, 'w') as outfile:
with open(ingest + '\\' + negative_end_file, 'w') as outfile:
    for i in result_negative:
        json.dump(i, outfile)
        outfile.write('\n')
total = []

total.extend(result_positive)
total.extend(result_negative)

# with open(ingest + '\\' + ingest_end_file, 'w') as outfile:
#      json.dump(total, outfile)

with open(ingest + '\\' + ingest_end_file, 'w') as outfile:
    for i in total:
        json.dump(i, outfile)
        outfile.write('\n')

# with open(negative_folder + '\\' + negative_end_file, 'w') as outfile:
#     json.dump(result_negative, outfile)
print('Complete.')