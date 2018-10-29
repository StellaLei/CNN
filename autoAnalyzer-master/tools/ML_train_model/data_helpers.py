import numpy as np
import re
import string
import itertools
from collections import Counter
import pdb
import commands
import os
import copy
count = 0

def delete_duplicate_cell(source):
    result = []
    for one in source:
        if one not in result:
            if one != "":
                result.append(one)
    return result


def generate_category_vec():
    train_cr_order = "./train_cr_order.txt"
    f_handle = open(train_cr_order,'r')
    data = f_handle.read()
    cr_list = data.split("\n")
    f_handle.close()
    cr_list_dic = {}
    count = 0
    lable_flag = []
    cr_list = delete_duplicate_cell(cr_list)
    for cr in cr_list:
        lable_flag.append(0)

    for cr in cr_list:
        lable_flag[count] = 1
        class_vec = copy.deepcopy(lable_flag)
        cr_list_dic[cr] = class_vec
        lable_flag[count] = 0
        count = count + 1
    return cr_list_dic

def filter_data(lines):
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

def clean_str(string):
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


def load_data_and_labels(positive_data_file, negative_data_file):
    """
    Loads MR polarity data from files, splits the data into words and generates labels.
    Returns split sentences and labels.
    """
    # Load data from files
    positive_examples = list(open(positive_data_file, "r").readlines())
    positive_examples = [s.strip() for s in positive_examples]
    negative_examples = list(open(negative_data_file, "r").readlines())
    negative_examples = [s.strip() for s in negative_examples]
    # Split by words
    x_text = positive_examples + negative_examples
    x_text = [clean_str(sent) for sent in x_text]

    # Generate labels
    positive_labels = [[0, 1] for _ in positive_examples]
    negative_labels = [[1, 0] for _ in negative_examples]
    y = np.concatenate([positive_labels, negative_labels], 0)
    return [x_text, y]



def load_journal_and_labels_eval(data_file_path,dev_sample_percentage):
    print "load data and labels"
    cr_list_dic = generate_category_vec()
    
    new_data_label = np.zeros(len(cr_list_dic))
    
    shell_cmd = "ls " + data_file_path
    result = commands.getstatusoutput(shell_cmd)
    cr_list = result[1].split("\n")

    #data_list = []
    x_train_text = []
    y_train_label = []
    x_dev_text = []
    y_dev_label = []
    err_msg_name_list = []

    y_cr = []
    count = 0
    for cr in cr_list:
        print cr
        x_list = []
        y_list = []
        cr_path = data_file_path + str(cr)
        shell_cmd = "ls " + cr_path
        result = commands.getstatusoutput(shell_cmd)
        all_files = result[1].split("\n")
        all_files = delete_duplicate_cell(all_files)
        err_list = []
        for file in all_files:
            file_path = cr_path + "/" + file
            print file_path
            if os.path.isfile(file_path):
                file_handle = open(file_path, "r")
#                data = file_handle.read()
#                file_handle.close()
#                data = clean_str(data)
                data = file_handle.readlines()
                #if data lines is bigger than 30000,then delete
                if len(data) > 10000:
                    continue
                file_handle.close()
                #pdb.set_trace()
                #data_list = filter_data(data)
                #data = clean_str("\n".join(data_list))
                data = clean_str("\n".join(data))
                x_list.append(data)
                err_list.append(file_path)
                if cr_list_dic.has_key(cr):
                    y_list.append(cr_list_dic[cr])
                else:
                    print "Err this msg can not find one-hot cr !!"
       
        if len(x_list) == 0:
            continue
        y_list = np.array(y_list)
        x_list = np.array(x_list)
        err_list = np.array(err_list)
        #pdb.set_trace() 
        np.random.seed(10)
        shuffle_indices = np.random.permutation(np.arange(len(y_list)))
        x_shuffled = x_list[shuffle_indices]
        y_shuffled = y_list[shuffle_indices]
        err_shuffled = err_list[shuffle_indices]

        divid_count = int(len(x_shuffled)*(1-dev_sample_percentage))
        x_train_text = np.append(x_shuffled[:divid_count],x_train_text)
        if len(y_train_label) == 0:
            y_train_label = y_shuffled[:divid_count]
        else:
            y_train_label = np.concatenate([y_shuffled[:divid_count],y_train_label],0)
        #pdb.set_trace()
        x_dev_text = np.append(x_shuffled[divid_count:],x_dev_text)
        if len(y_dev_label) == 0:
            y_dev_label = y_shuffled[divid_count:]
        else:
            y_dev_label = np.concatenate([y_shuffled[divid_count:],y_dev_label],0)
        err_msg_name_list = np.append(err_shuffled,err_msg_name_list)
    return [x_train_text,y_train_label,x_dev_text,y_dev_label,cr_list_dic,err_msg_name_list]



def store_train_cr_categary_order(cr):
    train_cr_order = "./train_cr_order.txt"
    f_handle = open(train_cr_order,'a')
    f_handle.write(cr + "\n")
    f_handle.close()
    return 

def load_journal_and_labels_train(data_file_path,dev_sample_percentage_rate):
    print "load data and labels"
    os.system("rm -rf ./train_cr_order.txt")
    dev_sample_percentage = dev_sample_percentage_rate
    shell_cmd = "ls " + data_file_path
    result = commands.getstatusoutput(shell_cmd)
    cr_list = result[1].split("\n")
    cr_list_dic = {}
    count = 0
    lable_flag = []
    for cr in cr_list:
        lable_flag.append(0)
    
    for cr in cr_list:
        store_train_cr_categary_order(cr)
        lable_flag[count] = 1
        class_vec = copy.deepcopy(lable_flag)
        cr_list_dic[cr] = class_vec
        lable_flag[count] = 0
        count = count + 1
    

    #data_list = []
    x_train_text = []
    y_train_label = []
    x_dev_text = []
    y_dev_label = []
    err_msg_name_list = []

    y_cr = []
    count = 0
    for cr,label in cr_list_dic.iteritems():
        print cr
        x_list = []
        y_list = []
        cr_path = data_file_path + str(cr)
        shell_cmd = "ls " + cr_path
        result = commands.getstatusoutput(shell_cmd)
        all_files = result[1].split("\n")
        err_list = []
        for file in all_files:
            file_path = cr_path + "/" + file
            print file_path
            if os.path.isfile(file_path):
                file_handle = open(file_path, "r")
                data = file_handle.readlines()
                #if data lines is bigger than 30000,then delete
                if len(data) > 10000:
                    continue
                file_handle.close()
                #pdb.set_trace()
                #data_list = filter_data(data)        
                #data = clean_str("\n".join(data_list))       
                data = clean_str("\n".join(data))
                err_list.append(file_path) 
                x_list.append(data)
                y_list.append(label)
        if len(x_list) == 0:
            continue
        y_list = np.array(y_list)
        x_list = np.array(x_list)
        err_list = np.array(err_list)
        #pdb.set_trace()
        np.random.seed(10)
        shuffle_indices = np.random.permutation(np.arange(len(y_list)))
        x_shuffled = x_list[shuffle_indices]
        y_shuffled = y_list[shuffle_indices]
        err_shuffled = err_list[shuffle_indices]
        #if amount of errmsg is little than 3 in one cr,
        #errmsg wil not be divided,directly put them into train dataset,
        #do not divided into verify dataset
        if len(x_list) < 3:
            dev_sample_percentage = 0
        else:
            dev_sample_percentage = dev_sample_percentage_rate

        divid_count = int(len(x_shuffled)*(1-dev_sample_percentage))

        x_train_text = np.append(x_shuffled[:divid_count],x_train_text)
        if len(y_train_label) == 0:
            y_train_label = y_shuffled[:divid_count]
        else:
            y_train_label = np.concatenate([y_shuffled[:divid_count],y_train_label],0)

        x_dev_text = np.append(x_shuffled[divid_count:],x_dev_text)
        if len(y_dev_label) == 0:
            y_dev_label = y_shuffled[divid_count:]
        else:
            y_dev_label = np.concatenate([y_shuffled[divid_count:],y_dev_label],0)
        err_msg_name_list = np.append(err_shuffled,err_msg_name_list)
    print cr_list_dic
    return [x_train_text,y_train_label,x_dev_text,y_dev_label,cr_list_dic,err_msg_name_list]


def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    #pdb.set_trace()
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data)-1)/batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]
