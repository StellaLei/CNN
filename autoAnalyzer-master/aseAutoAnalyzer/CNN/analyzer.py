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
#import data_helpers

from common.analyzer import Analyzer
from common.environment import Env
import common.basicApi as basicApi


class CNN(Analyzer):
    def __init__(self):
        basicApi.d_print('CNN_analyzer: __init__()')
        #initial analyzer
        self.checkpoint_dir = '%s/runs/checkpoints' % Env().getPath('CNN_HOME_PATH')
        self.err = []
        self.prediction_list = []
        self.train_cr_order = '%s/runs/train_cr_order.txt' % Env().getPath('CNN_HOME_PATH')

    def preProcess(self):
        basicApi.d_print('CNN_analyzer: preProcess()')
        FLAGS = tf.flags.FLAGS
        self.threshhold_min = -1
        self.threshhold_max = 7
        tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
        tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")
        self.vocab_path = os.path.join(self.checkpoint_dir, "..", "vocab")
        self.vocab_processor = learn.preprocessing.VocabularyProcessor.restore(self.vocab_path)
        
        self.cr_list_dic = self._generate_category_vec()
#        self.ckpt = tf.train.get_checkpoint_state(FLAGS.checkpoint_dir) 
#        self.ckpt_model = self.ckpt.model_checkpoint_path
        self.checkpoint_file = tf.train.latest_checkpoint(self.checkpoint_dir)
        #pdb.set_trace()
        self.graph = tf.Graph()
        with self.graph.as_default():
            session_conf = tf.ConfigProto(
              allow_soft_placement=FLAGS.allow_soft_placement,
              log_device_placement=FLAGS.log_device_placement)
            self.sess = tf.Session(config=session_conf)
            with self.sess.as_default():
                # Load the saved meta graph and restore variables
                self.saver = tf.train.import_meta_graph("{}.meta".format(self.checkpoint_file))
                #self.saver.restore(self.sess, self.ckpt_model)
                self.saver.restore(self.sess, self.checkpoint_file)
        
                # Get the placeholders from the graph by name
                self.input_x = self.graph.get_operation_by_name("input_x").outputs[0]
                # input_y = graph.get_operation_by_name("input_y").outputs[0]
                self.dropout_keep_prob = self.graph.get_operation_by_name("dropout_keep_prob").outputs[0]
        
                # Tensors we want to evaluate
                self.predictions = self.graph.get_operation_by_name("output/predictions").outputs[0]
        
                self.scores = self.graph.get_operation_by_name("output/scores").outputs[0]
        pass

    def analysing(self):
        basicApi.d_print('CNN_analyzer: analysing()')
        if self.task.caseList == []:
            #That means all test case pass
            pass
        else:
            storeJnlList = self.task.getStoreJnlList()
            input_list = self._filter_data(storeJnlList)
            x_list = self._transform_vector(input_list)
            self.prediction_list = self._prediction(x_list)
        pass

    def record(self):
        basicApi.d_print('CNN_analyzer: record()')
        for idx in xrange(len(self.task.caseList)):
            self.task.db.cateCNN.insertResult([self.task.caseList[idx][0], self.prediction_list[idx]])
        pass


    def _get_cr_number(self,flag):
        for cr,flag_vec in self.cr_list_dic.iteritems():
            target = np.argmax(flag_vec)
            if target == flag:
                return cr

    #delete duplicate character
    def _delete_duplicate_cell(self,source):
        result = []
        for one in source:
            if one not in result:
                if one != "":
                    result.append(one)
        return result

    def _generate_category_vec(self):
        f_handle = open(self.train_cr_order,'r')
        data = f_handle.read()
        cr_list = data.split("\n")
        f_handle.close()
        
        #pdb.set_trace()
        cr_list_dic = {}
        count = 0
        lable_flag = []
        for cr in cr_list:
            lable_flag.append(0)
    
        for cr in cr_list:
            lable_flag[count] = 1
            class_vec = copy.deepcopy(lable_flag)
            cr_list_dic[cr] = class_vec
            lable_flag[count] = 0
            count = count + 1
        return cr_list_dic

    def _filters(self,lines):
        content = []
        tmp = ''
        inCmdFlag = False
        for line in lines:
            if inCmdFlag:
                continue
            matched = re.match(r"^[0-9 |:]+(.*)", line)
            if matched:
                 tmp = matched.group(1)
                 #Remove lines which has DEBUG + TCL/SQL
                 if re.match(r'^DEBUG:.*:(TCL|SQL):.*\|[0-9]:.*', tmp):
                     continue
                 else:
                     #Remove lines which while command execute successful
                     matched = re.match(r"^DEBUG:.*\|[0-9]:(.*)", tmp)
                     if matched:
                         tmp = matched.group(1)
            #Remove all no used symble marks
            tmp = re.sub(r'''[(){}<>"'!:,.@+*/=\[\]\-\|]+''', ' ', tmp)
            #Check if during a successful command statment
            if re.match(r"^cmd_succeed", tmp):
                inCmdFlag = True
            if re.match(r'cmd_done$', tmp):
                inCmdFlag = False
            #Compose return value
            content.append(tmp)
        return content
    
    def _clean_str(self,string):
        """
        Tokenization/string cleaning for all datasets except for SST.
        Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
        """
        #print file_list[count]
        string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
        string = re.sub(r"\'s", " \'s", string)
        string = re.sub(r"\'ve", " \'ve", string)
        string = re.sub(r"n\'t", " n\'t", string)
        string = re.sub(r"\'re", " \'re", string)
        string = re.sub(r"\'d", " \'d", string)
        string = re.sub(r"\'ll", " \'ll", string)
        string = re.sub(r",", " , ", string)
        string = re.sub(r"!", " ! ", string)
        string = re.sub(r"\(", " \( ", string)
        string = re.sub(r"\)", " \) ", string)
        string = re.sub(r"\?", " \? ", string)
        string = re.sub(r"\s{2,}", " ", string)
        return string.strip().lower()
    

    def _calculate_fluctuation_value(self,character):
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

    def _prediction_cr(self,character_vec,output_predictions_vec):
        output_cr_list = []
        new_flag = "new"
        #pdb.set_trace()
        count = 0
        for character in character_vec:
            fluctuation_value = self._calculate_fluctuation_value(character)
            if fluctuation_value > self.threshhold_min and fluctuation_value < self.threshhold_max:
                #pre_cr = self._get_cr_number(np.argmax(character, axis=0))  
                pre_cr = self._get_cr_number(output_predictions_vec[count])
                output_cr_list.append(pre_cr)
            else:
                output_cr_list.append(new_flag)
            count = count + 1
        return output_cr_list

    def _prediction(self,input_list):
        #pdb.set_trace()
        output_scores_list = []
        output_scores,output_predictions = self.sess.run([self.scores,self.predictions], {self.input_x: input_list, self.dropout_keep_prob: 1.0})

        output_scores_list.extend(output_scores)
        output_cr_list = self._prediction_cr(output_scores_list,output_predictions)
        return output_cr_list

    def _batch_eval_prediction(self,input_list):
        output_prediction = self.sess.run(self.predictions, {self.input_x: input_list, self.dropout_keep_prob: 1.0})
        return output_prediction
 
    def _filter_data(self,file_name_list):
        input_list = []
        for file_name in file_name_list:
            file_handle = open(file_name, "r") 
            data_list = file_handle.readlines()
            file_handle.close()
            #data_list = self._filters(data)
            data = self._clean_str("\n".join(data_list))
            input_list.append(data)
        return input_list

    def _transform_vector(self,input_list):
        return np.array(list(self.vocab_processor.transform(input_list)))

    def update(self, task):
        self.setTask(task)
        # Down load tar ball from database
        self._downLoadTarball()
        pass

    def _downLoadTarball(self):
        tmpStorePath = '%s/cnnModel.tar.gz' % Env().getPath('TEMP_PATH')
        cnnModelPath = '%s/runs' % Env().getPath('CNN_HOME_PATH')
        rtl = self.task.db.cateCNN.searchCNNModel()
        #Here we need type tranlate, because hana return a buffer type.
        hexContext = str(rtl.getStr())
        binaryContext = hexContext.decode('hex')
        chmod = False
        if not os.path.exists(tmpStorePath):
            chmod = True
        with open(tmpStorePath, 'wb') as fd:
            fd.write(binaryContext)
        if chmod: 
             basicApi.chmodFile(tmpStorePath, 0777)
        cmd = '/usr/bin/rm -rf %s' % cnnModelPath
        os.system(cmd)
        cmd = '/bin/tar zxf %s -C %s' % (tmpStorePath, Env().getPath('CNN_HOME_PATH'))
        os.system(cmd)
        pass

