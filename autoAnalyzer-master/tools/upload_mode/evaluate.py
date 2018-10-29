import sys
sys.path.append('../../')


import tensorflow as tf
import numpy as np
import os
import time
import datetime
from tensorflow.contrib import learn
import csv
import math
import pdb
from math import log
from numpy import *
import commands
import copy
import re
from aseAutoAnalyzer.CNN.analyzer import CNN
import data_helpers
data_path = sys.argv[1]

def eval():
    global data_path
    prediction = CNN()
    #prediction.checkpoint_dir = "./runs/checkpoints/"
    #prediction.train_cr_order = "./runs/train_cr_order.txt"
    prediction.preProcess()
    dev_sample_percentage = 1
    batch_size = 30
    x_train_text, y_train, x_dev_text, y_dev ,cr_list_dic, err_msg_list = data_helpers.load_journal_and_labels_eval(data_path,dev_sample_percentage)
    x_raw = x_dev_text
    y_test = np.argmax(y_dev, axis=1)
    x_list = prediction._transform_vector(x_raw)
    batches = data_helpers.batch_iter(list(x_list), batch_size, 1, shuffle=False)
    all_predictions = []
    for x_test_batch in batches:
        prediction_list = prediction._batch_eval_prediction(x_test_batch)
        all_predictions.extend(prediction_list)
    correct_predictions = float(sum(all_predictions == y_test))
    print("Total number of test examples: {}".format(len(y_test)))
    print("Accuracy: {:g}".format(correct_predictions/float(len(y_test))))

def example_test():
    prediction = CNN()
    prediction.checkpoint_dir = "./runs/checkpoints/"
    prediction.train_cr_order = "./runs/train_cr_order.txt"
    prediction.preProcess()
    file_name_list = ["/remote/aseqa_archive2/mayu/machine_learning/Tensorflow/machine_learning_train/autoanalyzer/train/809999/ErrMsg_3385.jnl"]
    print file_name_list
    input_list = []
    for file in file_name_list:
        f_handle = open(file,'r')
        data = f_handle.read()
        input_list.append(data)
        f_handle.close()

    x_list = prediction._transform_vector(input_list)
    prediction_list = prediction._prediction(x_list)
    print prediction_list


eval()
#example_test()
