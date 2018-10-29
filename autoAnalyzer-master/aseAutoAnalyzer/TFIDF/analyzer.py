from common.analyzer import Analyzer
from common.environment import Env
import common.basicApi as basicApi
from multiprocessing import Manager
import aseAutoAnalyzer.TFIDF.tfidf as tfidf
import os
import re
import pdb

# This a global function which is used to calculation message vector
def calculateFeatureVec(dateTuple):
    itemId = dateTuple[0]
    extJnlDict = dateTuple[1]
    newFeatureDict = dateTuple[2]
    extJnl = extJnlDict[itemId]
    print('Calculating feature vector of %s ...' % itemId)
    curVec = tfidf.featureGenerator(extJnl, newFeatureDict)
    curVecStr = basicApi.vec2Str(curVec)
    return itemId, curVecStr

def wordFrequencyAnalysis(dateTuple):
    itemId = dateTuple[0]
    jnlName = dateTuple[1]
    stopWordDic = dateTuple[2]
    extJnlDict = dateTuple[3]
    kWordDict = dateTuple[4]
    print('Analysis journal of %s' % itemId)
    #jnlName = self.task.getJnlStoreName(itemId)
    #jnl = basicApi.readFile(jnlName)
    block = basicApi.openFile(jnlName, "r")
    filteBlock = _filteJnl(block)
    extJnl = tfidf.stemming(filteBlock, stopWordDic)
    extJnlDict[itemId] = extJnl
    #Find distinct words
    for word in extJnl.split():
        if kWordDict.has_key(word):
            continue
        else:
            kWordDict[word] = True

def _filteJnl(block):
    #pdb.set_trace()
    jnlBlock = []
    #Parse jnl file
    assertion = 'false'
    for line in block:
        #Begin to filt
        matched = re.match(r"^([0-9]*)\|([0-9]*)( )([0-9]*)( )([0-9]*)( )([0-9]*)( )([0-9]*)( )(0\d{1}|1\d{1}|2[0-3]):[0-5]\d{1}:([0-5]\d{1})\|(.*)\|([0-9]*):(.*)", line)
        if matched:
            jnlDetailList = matched.group(16)
            #Check if current test case are failed.
            if assertion == 'false':
                if re.match(r"DEBUG:QASQL:SQL.*",matched.group(14)) or re.match(r"DEBUG:QASQL:TCL.*",matched.group(14)) or re.match(r"DEBUG:QASQL:Connection.*",matched.group(14)) or     re.match(r"DEBUG:QASQL:async.*",matched.group(14)):
                    continue
                #Append to output jnl block
                jnlBlock.append(jnlDetailList + '\n')
        else:
            matched = re.match(r"^([0-9]*)\|([0-9]*)( )([0-9]*)( )([0-9]*)( )([0-9]*)( )([0-9]*)( )(0\d{1}|1\d{1}|2[0-3]):[0-5]\d{1}:([0-5]\d{1})\|(.*)", line)
            if matched:
                jnlDetailList = matched.group(14)

                if jnlDetailList.find('ASSERTION') != -1:
                    if assertion == 'false':
                        assertion = 'true'
                if jnlDetailList.find('assertion_id') != -1:
                    if assertion == 'true':
                        assertion = 'false'
                if assertion == 'false':
                    #Append to output jnl block
                    jnlBlock.append(jnlDetailList + '\n')
    return jnlBlock

class TFIDF(Analyzer):
    def __init__(self):
        basicApi.d_print('TFIDF_analyzer: __init__()')
        #initial analyzer
        self.stopWordsFile = '%s/stopword.txt' % Env().getPath('TFIDF_HOME_PATH')
        self.stopWordDic = {}
        self.featureDic = {}
        self.err = []

    def preProcess(self):
        basicApi.d_print('TFIDF_analyzer: preProcess()')
        #Get feature from db
        rtl = self.task.db.cateTFIDF.searchFeatureKey_tb()
        self.featureDic = rtl.getDict() 
        #Fill the stop words dict
        self._fillStopWordDic()
        pass

    def analysing(self):
        basicApi.d_print('TFIDF_analyzer: analysing()')
        for itemId,CaseName in self.task.caseList:
            jnlPath = self.task.getJnlStoreName(itemId)
            block = basicApi.openFile(jnlPath, "r")
            #Filter jnl block
            filteBlock = _filteJnl(block)
            #Simplify jnl block
            extractedJnl = tfidf.stemming(filteBlock, self.stopWordDic)
            msgVector = tfidf.featureGenerator(extractedJnl, self.featureDic)
            #Check msgVector
            if self._isZeroVec(msgVector):
                text = 'ERROR: Extracted journal file is empty, please manually analysis it.'
                self.err.append('%s\n%s\n'%(CaseName, text))
                #Write log into database
                self.task.db.cateTFIDF.insertNotAnalysis([itemId])
                continue
            #Find out all vectors
            rtl = self.task.db.cateTFIDF.searchAllVecs(itemId)
            allVecs = rtl.getDict()
            #Translate vector into string
            vecStr = basicApi.vec2Str(msgVector)
            if allVecs == {}:
                #Initial database
                self.task.db.cateTFIDF.insertTfidfResult([itemId, vecStr, '?'])
                continue
            #Insert current vector into database and attach it to exist CR if it has
            rtl = self.task.db.cateTFIDF.insertTfidfResult([itemId, vecStr, '?'])
            if rtl.getProcRtId() == 1:
                #If return value equal to 1 then means it is a new issue
                #First get all data from database
                if allVecs:
                    #Fuzzy search process begin
                    matched_tb = tfidf.fuzzySearch(msgVector, allVecs)
                    if matched_tb == {}:
                        #Should not run to here
                        text = 'ERROR: Not find any similarity vector.'
                        self.err.append('%s\n%s\n'%(CaseName, text))
                    else:
                        #Insert similarty table into db
                        for simVal,msgId in matched_tb.items():
                            self.task.db.cateTFIDF.insertSimilarity([itemId, str(msgId), str(simVal)])
                else:
                    #Database is empty, what we need to do, is just insert current message into databse.
                    text = 'WARNING: Database is empty now, we just directly insert current message as first itme.'
                    self.err.append('%s\n%s\n'%(CaseName, text))
        pass


    def record(self):
        basicApi.d_print('TFIDF_analyzer: record()')
        basicApi.appendFile(os.path.join(self.task.aaLogDir, 'autoAnalysis.log'), self.err)
        pass


    def _fillStopWordDic(self):
        stopwordsList = basicApi.openFile(self.stopWordsFile, 'r')
        for stwd in stopwordsList:
            self.stopWordDic[stwd.strip('\n')] = True

    def _isZeroVec(self, vec):
        sum = 0
        for index in range(0, len(vec)):
            sum += vec[index]
        if sum == 0:
            return True
        else:
            return False

    def update(self, task):
        #Recalculate TFIDF model
        print('Begin re-calculate TFIDF vectors ...')
        self.setTask(task)
        # Fill the stop words dict
        self._fillStopWordDic()
        # shared dictionary for multiprocess
        share = Manager()
        #Initial local variables
        self.stopWordDic = share.dict(self.stopWordDic)
        self.extJnlDict = share.dict()
        self.kWordDict = share.dict()
        self.newFeatureDict = share.dict()
        #Begin to update vector
        itemIdList = self._getItemIdList()
        self._updateFeatureKey(itemIdList)
        self._updateVector()
        print('Re-calculate TFIDF vectors complete.')
        pass

    def _getItemIdList(self):
        print('Syncing local stored journal file with database ...')
        storeJnlList = self.task.getAllStoreJnlList()
        rtl = self.task.db.cateCNN.searchItemIdList()
        itemIdList = rtl.getList()
        print('Local total store journal file: %s' % len(storeJnlList))
        print('Database total items number: %s' % len(itemIdList))
        #Check no used jnl files
        for itemId in itemIdList:
            jnlName = self.task.getJnlStoreName(itemId)
            if jnlName in storeJnlList:
                storeJnlList.remove(jnlName)
        #Delete jnl files not record in database
        print('Find miss match, delete local store files: %s' % len(storeJnlList))
        for jnlName in storeJnlList:
            basicApi.deleteFile(jnlName)
        return itemIdList

#    def _wordFrequencyAnalysis(self, itemId):
#        print('Analysis journal of %s' % itemId)
#        jnlName = self.task.getJnlStoreName(itemId)
#        jnl = basicApi.readFile(jnlName)
#        extJnl = tfidf.stemming(jnl, self.stopWordDic)
#        self.extJnlDict[itemId] = extJnl
#        #Find distinct words
#        for word in extJnl.split():
#            if self.kWordDict.has_key(word):
#                continue
#            else:
#                self.kWordDict[word] = True

    def _updateFeatureKey(self, itemIdList):
        print('Generating feature key ...')
        #Clean feature key table
        self.task.db.cateTFIDF.truncFeatureKey()
        #for itemId in itemIdList:
        #    self._wordFrequencyAnalysis(itemId)
        argList = []
        for itemId in itemIdList:
            jnlName = self.task.getJnlStoreName(itemId)
            arg = (itemId, jnlName, self.stopWordDic, self.extJnlDict, self.kWordDict)
            argList.append(arg)
        #paraller calculate word frequency
        basicApi.multiProcess(wordFrequencyAnalysis, argList)
        #Generate new feature key dictionary
        self.newFeatureDict = tfidf.if_generate(self.extJnlDict.values(), self.kWordDict.keys())
        #Update new feature key into database
        print('Update new feature key into database ...')
        for word,val in self.newFeatureDict.items():
            self.task.db.cateTFIDF.insertFeatureKey([word,val])
        pass

#    def _calculateFeatureVec(self, dateTuple):
#        itemId = dateTuple[0]
#        extJnl = dateTuple[1]
#        print('Calculating feature vector of %s ...' % itemId)
#        curVec = tfidf.featureGenerator(extJnl, self.newFeatureDict)
#        curVecStr = basicApi.vec2Str(curVec)
#        return itemId, curVecStr


    def _write2db(self, resultList):
        for result in resultList:
            itemId = result[0]
            curVecStr = result[1]
            task.db.cateTFIDF.updateMsgVector([itemId, curVecStr])

    def _updateVector(self):
        print('Re-calculateing vectors ...')
        #Recalculate vector here
        #Clean vectors in message table
        self.task.db.cateTFIDF.truncMsgVector()
        #Update recalculate result into database
        #for itemId,extJnl in self.extJnlDict.items():
        #    self._calculateFeatureVec((itemId,extJnl))
        argList = []
        for itemId in self.extJnlDict.keys():
            arg = (itemId, self.extJnlDict, self.newFeatureDict)
            argList.append(arg)
        #paraller calculate feature vectors
        rtl = basicApi.multiProcess(calculateFeatureVec, argList)
        self._write2db(rtl)
        #Clean message table, when VECTOR is NULL
        #NULL vector is because we use CNN record as stander,
        #So, when CNN record issue is less than TFIDF, then it will happen.
        self.task.db.cateTFIDF.cleanEmptyVector()
        pass
    pass
