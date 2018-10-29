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
from aseAutoAnalyzer.action import AseAction



if __name__ == '__main__':
    try:
        print('Begin action ...')
        action = AseAction()
        #This is the entry of update one hot vector
        #action.reCalculate()
        action.uploadCNN('./runs.tar')
        #
        print('End action ...')

    except basicApi.PROCESS_ERROR as err:
        print err

