"""
Run after map_generator.py
"""

import os
import shutil

magic_folder = 'D:\\mids\\data\\stage'

directories =[os.path.join(magic_folder, o).rsplit('\\')[-1] for o in os.listdir(magic_folder) 
                    if os.path.isdir(os.path.join(magic_folder,o))]


#todo - map hashes
print(directories)
positive_hashes = ['000c193f8e68018847b6d97befa5eaa4ce18be33',
                        '00b06dae33803c1f951d9835708b9b5418834ca6',
                        '00b8b9513172606012d5c59d826c53e79e2e13e6']
negative_hashes = directories[4:10]
print(positive_hashes)
print(negative_hashes)


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

print('complete.')