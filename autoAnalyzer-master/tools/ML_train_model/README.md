#this is prediction model train for autoanalyzer
#train
bash
nohup ./train.py --data_path=<train dataset folder>(for example nohup ./train.py --data_path="./train/")
#verify accuracy 
./eval_score.py --eval_train --checkpoint_dir="./runs/<file number>/checkpoints/" --data_path="./train/"
./eval_softmax.py --eval_train --checkpoint_dir="./runs/<file number>/checkpoints/" --data_path="./train/"
