#!/bin/sh
export SEED=239
export PYTHON150K_DIR=/workspace/project/limited
export DATA_DIR=/workspace/project/limited_output
export DESC=default
export CUDA=0
export SAVE_PATH=/project/model
pip install networkx
pip install rouge
pip install sklearn