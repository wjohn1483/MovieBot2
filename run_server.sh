#!/bin/bash

if [ ! -d "model_acc48" ]; then
    wget --no-check-certificate "https://speech.ee.ntu.edu.tw/~wjohn1483/MovieBot/model_acc48.zip"
    unzip model_acc48.zip
    rm model_acc48.zip
fi

CUDA_VISIBLE_DEVICES=1 python3 server.py
