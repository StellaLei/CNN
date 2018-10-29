import sys
sys.path.append('../../')
from common import basicApi 
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
import  codecs
from aseAutoAnalyzer.action import AseAction


def readFile(file_name):
    '''read file function'''
    #fin = codecs.open(file_name, "r", "utf-8")
    fin = codecs.open(file_name, "r")
    in_file = fin.readlines()
    fin.close()
    return in_file

def chmodFile(file_name, mode):
    os.system("chmod -R " + file_name + " " + mode)
    return

def writeFile(file_name, lines, mode = 0755):
    '''write file function'''
    #with codecs.open(file_name, 'w', "utf-8") as out_file:
    with codecs.open(file_name, 'w') as out_file:
        #pdb.set_trace()
        for line in lines:
           out_file.write(line)
    out_file.close()
    if mode != 0755:
        chmodFile(file_name, mode)


if __name__ == '__main__':
    try:
        print('Begin action ...')
        action = AseAction()
        #This is the entry of update one hot vector
        #pdb.set_trace()
        data_list = action.getCrItemIdPair() 
        lines = []
        for data in data_list:
            searchObj = re.search( r'\(\'(.+)\', (.+)\)',str(data), re.M|re.I)
            if searchObj:
                cr =searchObj.group(1)
                errmsgID = searchObj.group(2)
                cr_errmsgID = cr + ";" + errmsgID + "\n"
                lines.append(cr_errmsgID)
        writeFile("cr_errmsg.txt",lines)
        print('End action ...')

    except basicApi.PROCESS_ERROR as err:
        print err

