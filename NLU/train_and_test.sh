(time python3 ./NLU/codes/nlu_slot_filling_and_intent_prediction.py --train True) 2>&1 | tee ./NLU/log_train
(time python3 ./NLU/codes/nlu_slot_filling_and_intent_prediction.py --train False) 2>&1 | tee ./NLU/log_test
