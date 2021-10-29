#!/bin/bash
set -x

file_directory="/d/mids/ai_bug_detector/Closed_PR_files"
git_repo="/d/mids/matplotlib"
output_directory="/d/mids/real_parsed_data"
output_file="${output_directory}/jeff_is_the_realone.txt"

declare -a filePathList
declare -a fileList

fileList+=( "$( ls ${file_directory}/Closed_PR*.txt)" )
mkdir -p ${output_directory}


cd ${git_repo}
for file in ${fileList[@]}; do
	cd ${file_directory}
	#echo "Current Dir: $(pwd)"
	#echo "file = ${file}"
	#read -p pause
	for hash in $(cat ${file} | tr ' ' '\n' ) ; do 
		cd ${git_repo}
		git clean -ff
		sleep 1
		mkdir -p ${output_directory}/${hash}
		#read -p pause
		printf "================================\n" >> ${output_file}
		printf "Hash Commit: %s\n" ${hash} >> ${output_file}
		git checkout -f ${hash} 
		git diff HEAD^-1 --name-only >> ${output_directory}/temp_${hash}
		cat ${output_directory}/temp_${hash} | tee -a ${output_file}
		filePathList=( $(cat ${output_directory}/temp_${hash}) )
		#read -p pause
		for diff_file in ${filePathList[@]}; do 
			file_name=$(basename ${diff_file})
			cp ${diff_file} ${output_directory}/${hash}/${hash}_${file_name}
		done
		rm ${output_directory}/temp_${hash}
		git switch -
		git clean -ff
		sleep 1
	done
done


cleanup(){
unset file_directory git_repo output_directory output_file
unset filePathList fileList
rm -rf ${output_directory}
}

