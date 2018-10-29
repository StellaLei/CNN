import os
import codecs
import pdb
import string
import glob
import time
import numpy
import exceptions
import shutil
import platform
from multiprocessing import Pool as processPool
from multiprocessing.dummy import Pool as threadPool

def readFile(file_name):
    '''read file function'''
    #fin = codecs.open(file_name, "r", "utf-8")
    fin = codecs.open(file_name, "r")
    in_file = fin.readlines()
    fin.close()
    return in_file

def writeFile(file_name, lines, mode = 0777):
    '''write file function'''
    #with codecs.open(file_name, 'w', "utf-8") as out_file:
    with codecs.open(file_name, 'w') as out_file:
        for line in lines:
           out_file.write(line)
    out_file.close()
    cur_mode = oct(os.stat(file_name).st_mode)[-4:]
    if cur_mode != '0777':
        chmodFile(file_name, mode)

def appendFile(file_name, lines):
    '''write file function'''
    #with codecs.open(file_name, 'a', "utf-8") as out_file:
    with codecs.open(file_name, 'a') as out_file:
        for line in lines:
           out_file.write(line)
    out_file.close()

def deleteFile(fileName):
    if os.path.isfile(fileName):
        try:
            os.remove(fileName)
        except:
            pass

def deleteDir(dir):
    shutil.rmtree(dir, True)

def openFile(fileName, mode):
    #Because the files need to read in encoding with asicii, so we can not read in them with UTF-8.
    return codecs.open(fileName, mode)

def moveFile(fileName, target):
    if os.path.isfile(fileName):
        try:
            shutil.move(fileName, target)
        except:
            pass

def dirExist(dirPath):
    return os.path.exists(dirPath)

def makeDir(dirPath):
    os.mkdir(dirPath)

def execCmd(cmd):
    ''' execute the system command '''
    d_print(cmd)
    r = os.popen(cmd)
    out = r.read()
    r.close()

    #if not ('ps -ef' in cmd):
    #    print out
    return out

def chmodFile(fileName, mode):
    os.chmod(fileName, mode)

def getMachine():
    return platform.uname()[1]

def getLatestDir(dirList):
    dirDic = {}
    for dir in dirList:
        if os.path.isdir(dir):
            time = os.path.getmtime(dir)
            dirDic[time] = dir
    if dirDic == {}:
        return -1
    else:
        return dirDic[max(dirDic.keys())]

def getLatestFile(fileList):
    fileDic = {}
    for file in fileList:
        if os.path.isfile(file):
            time = os.path.getmtime(file)
            fileDic[time] = file
    if fileDic == {}:
        return -1
    else:
        return fileDic[max(fileDic.keys())]

def getFilesUnderDir(dir):
    files = glob.glob(dir)
    return files

def vec2Str(vec):
    rt_str = ''
    for var in vec:
        rt_str += str(var) + ','
    return rt_str[0:len(rt_str)-1]

def str2Vec(str):
    dataList = str.split(',')
    rt_vec = numpy.zeros(len(dataList))
    pos = 0
    for var in dataList:
        rt_vec[pos] = string.atof(var)
        pos += 1
    return rt_vec

''' this fucntion just for transfer db search result to dic,
    with style like [(var1,var2),(var1,var2),(var1,var2),...]'''
def list2Dic(s_list):
    rlt_dic = {}
    for var1, var2 in s_list:
        rlt_dic[var1] = var2
    return rlt_dic

def compress(str):
    return str.encode('zlib').encode('hex')

def decompress(cmpresdStr):
    return cmpresdStr.decode('hex').decode('zlib')

def parseDate(dateStr):
    date = False
    try:
        date = time.strptime(dateStr, '%Y/%m/%d')
    except:
        try:
            date = time.strptime(dateStr, '%m/%d/%Y')
        except:
            print 'Error: Datetime format wrong!'
    if date:
        return time.strftime('%Y/%m/%d', date)
    else:
        return date

def d_print(str):
    if os.environ.get('IA_DEBUG') == 'ON':
        print str

def quasrCmd(cmd):
    os.environ['QUASR_DRIVER'] = '/remote/quasr1/quasr/nightly/build/linux'
    return os.system(cmd)

class PROCESS_ERROR(Exception):
    pass

def multiProcess(func, argList):
    connPool = processPool(120)
    rtProcList = connPool.map(func, argList)
    connPool.close()
    connPool.join()
    return rtProcList

def multiThread(func, argList):
    connPool = threadPool(20)
    rtProcList = connPool.map(func, argList)
    connPool.close()
    connPool.join()
    return rtProcList

