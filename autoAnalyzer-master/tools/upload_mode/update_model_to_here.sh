#!/bin/sh

# example ./update_model_to_here.sh /remote/aseqa_archive2/mayu/machine_learning/Tensorflow/machine_learning_train/autoanalyzer/runs/1501742186/checkpoints 1500

# trained model checkpoint path
checkpoint_path=$1
echo $checkpoint_path
# model number which is used to predict
model_nub=$2
echo $model_nub

cr_order_path="$checkpoint_path/../../../train_cr_order.txt"
echo $cr_order_path

model1="$checkpoint_path/model-$model_nub.data-00000-of-00001"
echo $model1

model2="$checkpoint_path/model-$model_nub.index"
echo $model2

model3="$checkpoint_path/model-$model_nub.meta"
echo $model3

vocab="$checkpoint_path/../vocab"
echo $vocab

target_path="./runs"

echo "begin update"
cp -r $cr_order_path $target_path
chmod 755 "$target_path/train_cr_order.txt"

cp -r $vocab $target_path
chmod 755 "$target_path/vocab"

cp -r $model1 "$target_path/checkpoints/model-1.data-00000-of-00001"
chmod 755 "$target_path/checkpoints/model-1.data-00000-of-00001"

cp -r $model2 "$target_path/checkpoints/model-1.index"
chmod 755 "$target_path/checkpoints/model-1.index"

cp -r $model3 "$target_path/checkpoints/model-1.meta"
chmod 755 "$target_path/checkpoints/model-1.meta"

echo "begin tar"
tar -czvf ./runs.tar ./runs

