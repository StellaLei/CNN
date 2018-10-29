import getopt
import os
import sys
import pdb
import commands
import time
import string
import re
import stat
import sys
import time
import urllib
import urllib2
import codecs
from sgmllib import SGMLParser

def delete_duplicate_cell(source):
    result = []
    for one in source:
        if one not in result:
            if one != "":
                result.append(one)
    return result


def chmodFile(file_name, mode):
    os.system("chmod -R " + file_name + " " + mode)
    return


def readFile(file_name):
    '''read file function'''
    #fin = codecs.open(file_name, "r", "utf-8")
    fin = codecs.open(file_name, "r")
    in_file = fin.readlines()
    fin.close()
    return in_file

def writeFile(file_name, lines, mode = 0755):
    '''write file function'''
    #with codecs.open(file_name, 'w', "utf-8") as out_file:
    with codecs.open(file_name, 'w') as out_file:
        for line in lines:
           out_file.write(line)
    out_file.close()
    if mode != 0755:
        chmodFile(file_name, mode)


def is_closed_cr(cr):
    flag = 1
    (status,output) = commands.getstatusoutput('./check_cr_close_or_open.sh ' + cr)
    searchObj = re.search( r'New', output, re.M|re.I)
    if searchObj:
        flag = 0
    searchObj = re.search( r'Open', output, re.M|re.I) 
    if searchObj:
        flag = 0
    return flag

Lines_limitation = 30000
cr_err_file = "cr_errmsg.txt"
file_handle = open(cr_err_file,'r')
content = file_handle.read()
cr_err_lines = content.split("\n")
cr_err_lines = delete_duplicate_cell(cr_err_lines)
cr_list = []
for line in cr_err_lines:
    cr_err_list = line.split(";")
    cr = cr_err_list[0]
    cr_list.append(cr)
cr_list = delete_duplicate_cell(cr_list)

cr_match_dic = {}
#pdb.set_trace()
for cr_target in cr_list:
    err_ID_list = []
    for line in cr_err_lines:
        cr_err_list = line.split(";")
        cr = cr_err_list[0]
        err_ID = cr_err_list[1]
        if int(cr_target) == int(cr):
            err_ID_list.append(err_ID)

    cr_match_dic[cr_target] = err_ID_list

#pdb.set_trace()
print len(cr_match_dic)
cr_list = []
for cr,err_list in cr_match_dic.iteritems():
    count = 0
    print cr
    print len(err_list)
    print err_list

processed_data_path = "./processed_cr_data/"
source_data_path = "/remote/asepw_archive2/grid/autoAnalyzer/jnlMsgStorage/"
os.system("rm -rf " + processed_data_path)
os.system("mkdir " + processed_data_path)

cr_errmsg_num = 0
close_cr_list = []
for cr,err_list in cr_match_dic.iteritems():
    print "**********************************"
    count = 0
    print cr
    print "err msg nub:" + str(len(err_list))
    print err_list
    """
    if is_closed_cr(cr):
        print "this cr closed" 
        close_cr_list.append(cr)
        continue 
    """
    if len(err_list) <= cr_errmsg_num:
        #pdb.set_trace()
        continue

    flag = 0   
    cp_err_list = [] 
    for err_id in err_list:
        err_file = source_data_path + "ErrMsg_" + err_id + ".jnl"
        if os.path.isfile(err_file):
            file_data = readFile(err_file)
            if len(file_data) <= Lines_limitation:
                cp_err_list.append(err_file)
    print len(cp_err_list)
    if len(cp_err_list) != 0:
        cr_path = processed_data_path + cr
        os.system("mkdir " + cr_path)

        for err_file in cp_err_list:
            os.system("cp " + err_file + " " + cr_path) 
        cr_list.append(cr)
               
cr_list = delete_duplicate_cell(cr_list)
print len(cr_list)
print ",".join(cr_list)
print "closed cr list"
print ",".join(close_cr_list)

