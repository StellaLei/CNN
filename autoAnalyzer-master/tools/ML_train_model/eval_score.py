#! /usr/bin/env python

import tensorflow as tf
import numpy as np
import os
import time
import datetime
import data_helpers
from text_cnn import TextCNN
from tensorflow.contrib import learn
import csv
import math
import pdb
from math import log
from numpy import *
# Parameters
# ==================================================

# Data Parameters
min_threshhold = -1000
max_threshhold = 1000
#tf.flags.DEFINE_string("data_file", "./processed_cr_data_verify/", "Data source for data.")
tf.flags.DEFINE_string("data_file", "./processed_cr_data/", "Data source for data.")
tf.flags.DEFINE_float("dev_sample_percentage", 1, "Percentage of the training data to use for validation")

# Eval Parameters
tf.flags.DEFINE_string("data_path", "", "Data source for data.")
tf.flags.DEFINE_integer("batch_size", 1, "Batch Size (default: 64)")
tf.flags.DEFINE_string("checkpoint_dir", "", "Checkpoint directory from training run")
tf.flags.DEFINE_boolean("eval_train", False, "Evaluate on all training data")

# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")


FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
print("\nParameters:")
for attr, value in sorted(FLAGS.__flags.items()):
    print("{}={}".format(attr.upper(), value))
print("")

# Load data
print("Loading data...")
#x_text, y = data_helpers.load_data_and_labels(FLAGS.positive_data_file, FLAGS.negative_data_file)
x_train_text, y_train, x_dev_text, y_dev ,cr_list_dic, err_msg_list = data_helpers.load_journal_and_labels_eval(FLAGS.data_path,FLAGS.dev_sample_percentage)
# Build vocabulary


x_raw = x_dev_text
y_test = np.argmax(y_dev, axis=1)

# Map data into vocabulary
vocab_path = os.path.join(FLAGS.checkpoint_dir, "..", "vocab")
vocab_processor = learn.preprocessing.VocabularyProcessor.restore(vocab_path)
x_test = np.array(list(vocab_processor.transform(x_raw)))

print("\nEvaluating...\n")

def similarity_calculator(feature1, feature2):
    length1 = sqrt(vdot(feature1,feature1))
    length2 = sqrt(vdot(feature2,feature2))
    #if length1*length2 == 0:
    #    return 0
    return vdot(feature1,feature2)/(length1*length2)

def fuzzySearch(curFeature, featureDic):
    dic_Dis2Feature = {}
    rtlist = []
    for k_var, f_var in featureDic.items():
        f_distance = similarity_calculator(curFeature,f_var)
        if len(dic_Dis2Feature) < 5:
            dic_Dis2Feature[f_distance] = k_var
        else:
            minKey = sorted(dic_Dis2Feature.keys())[0]
            if minKey < f_distance:
                del dic_Dis2Feature[minKey]
                dic_Dis2Feature[f_distance] = k_var
    return dic_Dis2Feature

def get_cr_number(flag):
    global cr_list_dic
    for cr,flag_vec in cr_list_dic.iteritems():
        target = np.argmax(flag_vec)
        if target == flag:
            return cr

def get_cr_vec(cr):
    global cr_list_dic
    return np.argmax(cr_list_dic[cr])

def calculate_fluctuation_value(character):
    max_value = max(character)
    #pdb.set_trace()
    sum_rest = 0
    for one in character:
        if one == max_value:
            continue
        else:
            sum_rest = sum_rest + one
    mean_value_test = sum_rest/(len(character) - 1)
    return (max_value - mean_value_test)/max_value

def classify_and_prediction(character_vec):
    global y_test
    global err_msg_list
    global result_classify
    global min_threshhold
    global max_threshhold
    need_to_build_class_msg_id_list = []
    mistake_category_dic = {}
    count = 0
    fluctuation_value_list = []
    for character in character_vec:
        fluctuation_value = calculate_fluctuation_value(character[0])
        fluctuation_value_list.append(fluctuation_value)
    fluctuation_value_list.sort()
    print fluctuation_value_list

    for character in character_vec:
        #print err_msg_list[count]
        #print character
        fluctuation_value = calculate_fluctuation_value(character[0])
        #print fluctuation_value
        #pdb.set_trace()
        if fluctuation_value > min_threshhold and fluctuation_value < max_threshhold:
            #pdb.set_trace()
            result_classify = np.concatenate([result_classify,np.argmax(character, axis=1)])
            true_cr = get_cr_number(y_test[count])
            pre_cr = get_cr_number(np.argmax(character, axis=1))
            print('\033[0;32;48m')
            print err_msg_list[count] + "[original cr:" + str(true_cr) + "]---->" + "predictable cr:" + str(pre_cr)
            print('\033[0m')

            if true_cr != pre_cr:
                mistake_category_dic[err_msg_list[count]] = [true_cr,pre_cr]
            count = count + 1
        else:
            #if count < len(y_test):
                #pdb.set_trace()
            result_classify = np.concatenate([result_classify,np.array([y_test[count]])])
            need_to_build_class_msg_id_list.append(err_msg_list[count])
            count = count + 1
    print "*******************************REPORT SUMMARY******************************"
    print "[1] Train  dataset amount:               [1000]"
    print "[2] Verify dataset amount:               [" + str(len(character_vec)) + "]"
    print "[3] Right classifying amount:            [" + str((len(character_vec) - len(mistake_category_dic))) + "]" 
    print "[4] Mistake classifying amount:          [" + str(len(mistake_category_dic)) + "]"
    print "[5] New problems need to report new CR:  [" + str(len(need_to_build_class_msg_id_list)) + "]"
    print "***************************************************************************"
    print('\033[0;32;48m')

    print "******************************* Report New CR *****************************"
    if len(need_to_build_class_msg_id_list) == 0:
        msg = ""
    else:
        msg = "\n"
        for one in need_to_build_class_msg_id_list:
            msg = msg + " " + one
    print msg
    print "\n***************************************************************************"
    print('\033[0m')
    print('\033[0;31;48m')
    print "******************************* Err  Info ***********************************\n"
    for Errmsg,cr_list in mistake_category_dic.iteritems():
        print Errmsg + "[original cr:" + str(cr_list[0]) + "]---->" + "predictable cr:" + str(cr_list[1])

    #print('*' * 50)
    print "\n***************************************************************************"
    print('\033[0m')
    return


# Evaluation
# ==================================================
checkpoint_file = tf.train.latest_checkpoint(FLAGS.checkpoint_dir)
graph = tf.Graph()
with graph.as_default():
    session_conf = tf.ConfigProto(
      allow_soft_placement=FLAGS.allow_soft_placement,
      log_device_placement=FLAGS.log_device_placement)
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        # Load the saved meta graph and restore variables
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        # Get the placeholders from the graph by name
        input_x = graph.get_operation_by_name("input_x").outputs[0]
        # input_y = graph.get_operation_by_name("input_y").outputs[0]
        dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

        # Tensors we want to evaluate
        predictions = graph.get_operation_by_name("output/predictions").outputs[0]

        scores = graph.get_operation_by_name("output/scores").outputs[0]
       
        #h_pool_flat = graph.get_operation_by_name("h_pool_flat").outputs[0] 
        # Generate batches for one epoch
        batches = data_helpers.batch_iter(list(x_test), FLAGS.batch_size, 1, shuffle=False)

        
        # collect the main character vec
        all_character_vec = []
        category_character_dic = {}
        result_classify = []
        for x_test_batch in batches:
            batch_scores = sess.run(scores, {input_x: x_test_batch, dropout_keep_prob: 1.0})
            all_character_vec.append(batch_scores)

        classify_and_prediction(all_character_vec)
        #pdb.set_trace()
        correct_predictions = float(sum(result_classify == y_test))
        
        #print("Total number of test examples: {}".format(len(y_test)))
        print('\033[1;34;48m')
        print("Accuracy: [3]/[2] = {:g}".format(correct_predictions/float(len(y_test))))
        print('\033[0m')

