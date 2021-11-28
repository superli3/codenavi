"""
Run after map_generator.py
"""

import os
from distutils.dir_util import copy_tree
import shutil
import pandas as pd
from random import sample
import time


#sampling_multiplier = 5
sampling_multiplier = 1
source_folder = 'D:\\mids\\real_parsed_data'
magic_folder = 'D:\\mids\\data\\stage'
mapping = pd.read_csv('mapping.csv')

magic_folder_directories =[os.path.join(magic_folder, o).rsplit('\\')[-1] for o in os.listdir(magic_folder) 
                    if os.path.isdir(os.path.join(magic_folder,o))]

source_folder_directories =[os.path.join(source_folder, o).rsplit('\\')[-1] for o in os.listdir(source_folder) 
                    if os.path.isdir(os.path.join(source_folder,o))]

print(time.ctime())
# for hash in source_folder_directories:
#     copy_tree(source_folder + '\\' + hash, magic_folder + '\\' + hash)
    #print(source_folder + '\\' + hash)
print(time.ctime())


positive_hashes = mapping[mapping['Label'] == 'Positive']['sha'].to_list()
negative_hashes = sample(mapping[mapping['Label'] == 'Negative']['sha'].to_list(), len(positive_hashes * sampling_multiplier))




#Mover
for hash in positive_hashes:
    try:
        files = os.listdir(magic_folder + '\\' + hash)

        #purge non.py files
        for file in files:
            file_ext = file[-3:]
            if file_ext != '.py':
                os.remove(magic_folder + '\\' + hash + '\\' + file)

        #move to folder in question
        os.rename(magic_folder + '\\' + hash, magic_folder + '\\positive\\' + hash)
    except:
        print(f'error for hash: {hash} - continuing to the next one.')

for hash in negative_hashes:
    try:
        files = os.listdir(magic_folder + '\\' + hash)

        #purge non.py files
        for file in files:
            file_ext = file[-3:]
            if file_ext != '.py':
                os.remove(magic_folder + '\\' + hash + '\\' + file)

        #move to folder in question
        os.rename(magic_folder + '\\' + hash, magic_folder + '\\negative\\' + hash)
    except:
        print(f'error for hash: {hash} - continuing to the next one.')

print('complete.')