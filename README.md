# CodeNavi

This is the repo for CodeNavi, a framework for applying neural net based langauge models to software projects, in order to help software developers identify bugs and ship better code.

I worked on this project as part of my UC Berkely MIDS class - Natural Language Processing with Deep Learning

Paper here: [review]

## Overview

This project contains the files for Can You Review My Pull Request, a framework to assist software developers review code by using Natural Language Processing techniques applied to code.

It is inspired from the following video, as well as the current domain I work in:

[![how we write/review code in big tech companies](https://img.youtube.com/vi/rR4n-0KYeKQ/0.jpg)](https://www.youtube.com/watch?v=rR4n-0KYeKQ "how we write/review code in big tech companies")

In large established software development projects, bugs can be costly. [A IBM study](https://www.celerity.com/the-true-cost-of-a-software-bug) found that bugs can be 5x more costly to identify & fix after it is deployed, compared to being identified in the design phase. Software development can be fast moving, complicated, and confusing. Technical details may be siloed with certain developers, and information on technical details may be lost over time. Common industry practices involve structured processes such as CI/CD, and testing framework - this project aims to expand on the existing frameworks to help reduce the rise of recurring bugs in software projects.

The purpose of this project is to create a framework which analyzes a software project's history of pull requests, and trains a language model to assess the particular risk of introducing an issue or problematic code into the main/master branch. The score will then be presented to developers as a way to help them review individual pull requests.

# Machine Learning Pipeline Overview

The process of converting the underlying history of code changes for a project into a format that is understandable by a language model is quite complex and involved. The overall process is outlined below:

## 1) Pick a project of interest - project requirements

An important aspect here is that the project has a long history of committers and contributors. Additionally, you will need to be able to label Pull Request accordingly. For the project, I have picked out matplotlib, however, any project in particular will do.

![Matplotlib Pull Requests](/images/Pull_Requests.PNG?raw=true "Matplotlib Pull Requests")


![Matplotlib Issues](/images/issues.PNG?raw=true "Matplotlib Issues")

Matplotlib has an extensive history of pull requests (10k+), as well has a long history of closed issues which link back to pull requests.

I went through and manually labeled a dataset, however, depending on how the discussion around a project is formatted, it may be conducive to create an additional framework to scrape and label this data automatically.

An additional consideration here is that you will wnat to

## 2) Scrape the data

Data was scraped using the [GitHub Pull Request API](https://docs.github.com/en/rest/reference/pulls). From this API, several important fields were pulled from the resulting API 

The commit hash associated with the pull request ID, required for git to pull up the information in question
The corresponding .diff file, which shows which files were changed as part of the pull request.
Isolate the files that were changed as part of each merge request

You can run PR_api_request.py to scrape the necessary files.

Github has a rate limiting mechanism, so it is recommended to perform the API call in conjuction with a user generated [PAT token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

```
python PR_api_request.py <your user generated PAT token>
```

Once the raw json data has been scraped, you will want to extract the files that were changed for each individual pull request. A flow chart of this process is provided below, for 1 hash iteration


![Git Scraper flow chart](/images/git_flow_chart.png?raw=true "Flowchart")

This process will be repeated multiple times via the bash script git_scraper.sh

```
.\git_scraper.sh
```

## 3) Label the data.

Labels are a key part of any Machine Learning project.

After scraping the files, you will want to parse them into the individual files. You will want to generate a list of files.

You can review labeled_bugs.csv to get an idea of the schema. Issues that have been mapped to individual pull requests will be considered "positives", otherwise, we will consider the pull request as "negative".


## 4) Data preprocessing.
Once we have scraped the files associated with each individual pull request, we will want to process the data in a way that it can be understood by a language model. For the purpose of this project, I have decided to go with an abstract syntax tree approach.

We will want to map the unique Pull Request ID to the corresponding hash. Once the files have been mapped, we will want to separate the files into individual "positive" and "negative" folders.

The first step here is to parsing the individual code into [abstract syntax trees](https://en.wikipedia.org/wiki/Abstract_syntax_tree). 


```
## Parse positive files

# Enter docker container
docker run -it --entrypoint /bin/bash  -v d:/mids/data/positive:/home 082ebf62f850

# Execute script to generate asts within the docker container
./ast_generator.sh

## Parse Negative files

# Enter docker container
docker run -it --entrypoint /bin/bash  -v d:/mids/data/negative:/home 082ebf62f850

# Execute script to generate asts within the docker container
./ast_generator.sh
```


```
## convert files
```



# Model training

I will be using an approach based on the outlook referenced in the seq2seq paper. We have generated our labels and sequences, so the next step will be to utilize a language model that can adequately 

## Setting up a VM

The model was trained on AWS. Due to the cost of a GPU based instance on AWS, the data was preprocessed locally. Once it was finished processing, it was tar'd and uploaded to an S3 bucket, where it found it's way AWS GPU based instance. I used the [Nvidia Deep Learning AMI on AWS](https://aws.amazon.com/marketplace/pp/prodview-e7zxdqduz4cbs), as well as the [Nvidia Tensorflow docker container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/tensorflow).

The VM instance in particular used was a g4dn.xlarge instance with a T4 GPU. An additional storage space of 1TB was also provisioned for the VM instance. 


```

# command to connect to the vm
ssh -i "w251-ec2.pem" ubuntu@<ec2 instance dns>.compute-1.amazonaws.com

# pull docker container
docker pull nvcr.io/nvidia/tensorflow:21.10-tf2-py3

# mount any additional storage provisioned by VM
sudo mount /dev/nvme1n1 /home/ubuntu/storage

# clone file
https://superli3w251.s3.amazonaws.com/limited.tar

# pull the files on the tar'd VM
sudo wget <location of tar'd data>

### run docker container ###

## tf 2
docker run --gpus all -it --rm -v "/home/ubuntu/project":"/workspace/project" -p 8888:8888 nvcr.io/nvidia/tensorflow:21.10-tf2-py3

## tf 1
docker run --gpus all -it --rm -v "/home/ubuntu/project":"/workspace/project" -p 8888:8888 nvcr.io/nvidia/tensorflow:21.10-tf1-py3

# run docker container without mounted storage, if needed
docker run --gpus all -it --rm -p 8888:8888 nvcr.io/nvidia/tensorflow:21.10-tf1-py3

## run script
source /workspace/project/codenavi/vm_env.sh

chmod +x preprocess.sh
./preprocess.sh $DATA_DIR

# run jupyter lab
jupyter lab

# pull this repo onto the vm
git clone https://github.com/superli3/codenavi.git

# pull github repo for code2seq (note - only works with tf1 container)
git clone https://github.com/tech-srl/code2seq.git

# docker container
ip instance:8888 

# pull files onto vm
wget <url to tar'd files processed by json_to_seq_v2.py>

# untar files
tar -xvf limited.tar

# set vm environment variables
source vm_env.sh

#From Python150KExtractor from code2seq repo, preprocess data for training
./preprocess.sh $DATA_DIR

# Train (modify config.py in code2seq repo, as needed)
# set PATIENCE to 300
# set MAX_PATH_LENGTH to length of sequences generated by json_to_seq
# set MAX_TARGET_PARTS to 1
# set TARGET_VOCAB_MAX_SIZE to 2

# from code2seq repo
./train_python150k.sh $DATA_DIR $DESC $CUDA $SEED

```




## Papers

I've pasted some papers below which helped in understanding this domain better.

Code2Seq: Generating Sequences from Structured Representations of Code - Uri Alon, Shaked Brody, Omer Levy, Eran Yahav - https://arxiv.org/abs/1808.01400

DeepBugs: A Learning Approach to Name-based Bug Detection - Michael Pradel, Koushik Sen - https://arxiv.org/abs/1805.11683

Neural Software Analysis - Michael Pradel, Satish Chandra - https://arxiv.org/abs/2011.07986

Evaluating Large Language Models Trained on Code - Chen, et al. - https://arxiv.org/abs/2107.03374

## Questions? Concerns? Feedback?

Happy to hear it - please feel free to drop a line in the issues section, or email me directly.
