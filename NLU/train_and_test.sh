#! /bin/bash -xe
if [ $# -ne 1 ]; then
    echo "Usage:"
    echo "    bash $0 <device number>"
    echo "E.g."
    echo "    bash $0 0"
    exit 1
fi
export CUDA_VISIBLE_DEVICES=$1 
(time python3 ./NLU/codes/nlu_slot_filling_and_intent_prediction.py --train True) 2>&1 | tee ./NLU/log_train
(time python3 ./NLU/codes/nlu_slot_filling_and_intent_prediction.py --train False) 2>&1 | tee ./NLU/log_test
