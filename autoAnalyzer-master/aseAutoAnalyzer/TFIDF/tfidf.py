import common.basicApi as basicApi
from math import log
from numpy import *
from poterStemming import *
import re
import pdb

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
        f_distance = similarity_calculator(curFeature,basicApi.str2Vec(f_var))
        if len(dic_Dis2Feature) < 5:
            dic_Dis2Feature[f_distance] = k_var
        else:
            minKey = sorted(dic_Dis2Feature.keys())[0]
            if minKey < f_distance:
                del dic_Dis2Feature[minKey]
                dic_Dis2Feature[f_distance] = k_var
    return dic_Dis2Feature
    #rtlist = dic_Dis2Feature.values()
    #rtlist.reverse()
    #return rtlist

def featureGenerator(str, keyWordsDic):
    doc_tokens = re.split('[:|/" "]', str.lower())
    keyWordsList = sorted(keyWordsDic.keys())
    feature_vector = zeros(len(keyWordsList))
    for word in keyWordsList:
        feature_vector[keyWordsList.index(word)] = tf_idf(word, doc_tokens, keyWordsDic)
    return feature_vector

# Returns the float Term Frequency - Inverse Document Frequency or tf-idf
def tf_idf(term, document_tokens, document_tokens_list):
        return term_frequency(term, document_tokens) * inverse_document_frequency(term, document_tokens_list)

def inverse_document_frequency(term, document_tokens_list):
        a=document_tokens_list[term]
        if a==0:
            a=1
        return 3/ float(a)

# Returns float term frequency (TF),
# normalized for document size
# tf = term count / token count
def term_frequency(term, document_tokens):
    return term_count(term, document_tokens) / float(token_count(document_tokens))

# Returns integer Term Count for a document
# tc = count number of term occurence in document
def term_count(term, document_tokens):
#       return document_tokens.count(term.lower())
        return document_tokens.count(term)

# Returns integer with total number of tokens in a document
# toc = count number of tokens in a document
def token_count(document_tokens):
    return len(document_tokens)

def if_generate(errMsgs, keyWords):
    feature_vector = [0]*len(keyWords)
    index_weight={}
    for msg in errMsgs:
        #if msg == '\n':
        document_tokens = re.split('[:|/" "\n]' ,msg.lower())
        for word in keyWords:
            if term_count(word, document_tokens) > 0:
                feature_vector[keyWords.index(word)] += 1
        continue
        #else:
        #    string = string + ' ' + line
    for word in keyWords:
        index_weight[word] = feature_vector[keyWords.index(word)]
    return index_weight

# Extract case jnl into extracted jnl
# Use keywords stemming method
def stemming(msgList, stopwordDic):
    stemObj = PorterStemmer()
    validReg = '[^A-Za-z]'
    extractMsg = ''
   
    cmd_fail_flag = 0
    clientmsg_flag = 0
    servermsg_flag = 0
    command_flag = ''
    header_flag = '' 
    startprocess_flag = ''
    matched_command = ''
    startprocess_cmd = ''
    blank_space = ' +'
    for line in msgList:
        word = ''
        if line.find('deletefile') != -1:
            continue
        matched = re.match('.*statprocess( *)([0-9]+)',line)
        if matched:
            continue
        if line.find('startprocess') != -1:
            line = line.strip()
            line = line.strip('\n')
            startprocess_cmd = line
            #matched = re.match('.*startprocess ({.*?}) ({.*?}) (.*) ({.*?}) ({{.*}}) ({.*?})',line)
            matched = re.match('.*startprocess ({.*?}) (.*) ({{.*} *}) ({.*?})',startprocess_cmd)
            if matched:
                startprocess_flag = 'flase'
                startprocess_cmd = ''
                continue
            else:
                startprocess_flag = 'true'
                continue
        if startprocess_flag == 'true':
            line = line.strip()
            line = line.strip('\n')
            if line == '':
                continue
            else:
                startprocess_cmd = startprocess_cmd + ' ' +line
                #matched = re.match('.*startprocess ({.*?}) ({.*?}) (.*) ({.*?}) ({{.*}}) ({.*?})',startprocess_cmd)
                matched = re.match('.*startprocess ({.*?}) (.*) ({{.*} *}) ({.*?})',startprocess_cmd)
                if matched:
                    startprocess_flag = 'flase'
                    startprocess_cmd = ''
                    continue
                else:
                    continue
        #line = re.sub(validReg," ",line)
        #line = re.sub(blank_space," ",line)
        
        if line == '':
            break
        if line.find('testcase code') != -1 or line.find('assertion') != -1 or line.find('qas connect') != -1:
            continue
        if line.find('sqlsa callback') != -1 :
            continue
        if line.find('sqlsa moreresults') != -1 :
            continue
        if line.find('sqlsa continue') != -1 :
            continue
        if line.find('sqlsa command') != -1 :
            matched = re.match(r'.*command( +)(.*)',line)
            matched_command = matched.group(2)
            matched_command = matched_command.strip()

            command_flag = 'true'
            continue
        if command_flag == 'true':
            if line.find(matched_command) == -1:
                continue
            else:
                command_flag = 'false'
                continue
        if line.find('header') != -1 or line.find('cmd_succeed') != -1 or re.match('{ *status 0',line):
            if line.find('done') != -1:
                header_flag = 'flase'
                continue
            else:
                header_flag = 'true'
                continue
        if header_flag == 'true':
            if line.find('done') == -1:
                continue
            else:
                header_flag = 'flase'
                continue
        if re.match('{ *servermsg',line):
            if line.find('5701'):
                servermsg_flag = servermsg_flag | 1
                if re.match('.*} *}',line):
                    servermsg_flag = servermsg_flag ^ 1
                    continue
                else:
                    continue
        if servermsg_flag != 0:
            if servermsg_flag & 1 != 0:
                if re.match('.*} *}',line):
                    servermsg_flag = servermsg_flag ^ 1
                    continue
                else:
                    continue
        if re.match('{ *clientmsg',line):
            clientmsg_flag = clientmsg_flag | 1
            if re.match('.*} *} *}',line):
                clientmsg_flag = clientmsg_flag ^ 1
                continue
            else:
                continue
        if clientmsg_flag != 0:
            if clientmsg_flag & 1 != 0:
                if re.match('.*} *} *}',line):
                    clientmsg_flag = clientmsg_flag ^ 1
                    continue
                else:
                    continue

        if re.match('cmd_fail',line):
            if line.find('SHUTDOWN'):
                cmd_fail_flag = cmd_fail_flag | 1
                if re.match('.*} *} *}',line):
                    cmd_fail_flag = cmd_fail_flag ^ 1
                    continue
                else:
                    continue
        if cmd_fail_flag != 0:
            if cmd_fail_flag & 1 != 0:
                if re.match('.*} *} *}',line):
                    cmd_fail_flag = cmd_fail_flag ^ 1
                    continue
                else:
                    continue

        line = re.sub(validReg," ",line)
        line = re.sub(blank_space," ",line)
        for char in line:
            if char.isalpha():
                word += char.lower()
            else:
                if word:
                    if not stopwordDic.has_key(word):
                        extractMsg += stemObj.stem(word, 0,len(word)-1)
                    word = ''
                extractMsg += char.lower()
   # for line in msgList:
   #     word = ''
   #     line = re.sub(validReg," ",line)
   #     if line == '':
   #         break
   #     if line.find('command') != -1 or line.find('header') != -1 or line.find('succeed') != -1 or line.find('testcase code') != -1:
   #         continue
   #     for char in line:
   #         if char.isalpha():
   #             word += char.lower()
   #         else:
   #             if word:
   #                 if not stopwordDic.has_key(word):
   #                     extractMsg += stemObj.stem(word, 0,len(word)-1)
   #                 word = ''
   #             extractMsg += char.lower()
    basicApi.d_print(extractMsg)
    return extractMsg
