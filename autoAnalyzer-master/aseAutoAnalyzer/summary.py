from common.summary import Summary
from actions.mail import TestsetReport
import common.basicApi as basicApi
from actions.updateTRD import UpdateTRD
import pdb

class AseSummary(Summary):
    def __init__(self):
        basicApi.d_print('AseSummary: __init__()')

    def sum(self):
        # Read prediction from each DB and merge them together.
        basicApi.d_print('AseSummary: sum()')
        if self.task.caseList == []:
            #If the claseList is empty, then that means test case all pass.
            print('AseSummary: Test case all pass, Skip summary')
            return True
        #1, search TFIDF result DB, find out all simulate testcases and group them together.
        #Just update failed test case for current test set.
        #self.task.db.cateSummary.updateCluster()
        self.task.db.cateSummary.updateCluster([self.task.testSet])
        #2, Search CNN result DB, get all data.
        rtl = self.task.db.cateSummary.searchCNNResult([self.task.tag,
                                                        self.task.platform,
                                                        self.task.branch,
                                                        self.task.testSet,
                                                        self.task.tagTime])
        #rtl = self.task.db.cateSummary.searchCNNResult_x()
        CNNResultDict= rtl.getDict()
        #3, Check CNN prediction result with TFIDF group by decision tree.
        for itemId in CNNResultDict.keys():
            cnnCR = CNNResultDict[itemId]
            rtl = self.task.db.cateSummary.searchClusterIdByItemId(itemId)
            if rtl.isEmpty():
                #Can not find current itemId in cluster.
                #That means TFIDF do not process this itemId.
                #In this case, we directly trust CNN result.
                self._updateCR(itemId, cnnCR)
            else:
                clusterId = rtl.getStr()
                rtl = self.task.db.cateSummary.searchItemsByClusterId(clusterId)
                itemIdList = rtl.getList()
                #Get related CR list by item list
                cnnCrList = self._getCNNPredictResult(itemIdList)
                #for item in itemIdList:
                if self._isAllSame(cnnCrList):
                    #All same situation no need further analysis
                    self._updateCR(itemId, cnnCrList[0])
                else:
                    #Partily same
                    if self._isNewMoreThanHalf(cnnCrList):
                        #New issue more than 50%
                        #Attach all issue as new
                        self._updateCR(itemId, 'new')
                    else:
                        #new less equal than 50%
                        maxCr = self._isSameCRMoreThanHalf(cnnCrList)
                        if maxCr:
                            #Attach to same CR
                            self._updateCR(itemId, maxCr)
                        else:
                            #If CNN partly same with most TFIDF result
                            maxCr = self._ispartlySameWithMostTFIDF(itemIdList, cnnCrList)
                            if maxCr:
                                #Auto attach to most possibility
                                self._updateCR(itemId, maxCr)
                            else:
                                #manual analysis
                                self._updateCR(itemId, 'new')
        #Send mail to test set owner
        tsr = TestsetReport(self.task)
        tsr.execute()

    def _getCNNPredictResult(self, itemIdList):
        crList = []
        for itemId in itemIdList:
            rtl = self.task.db.cateSummary.searchCNNcrByItemId(itemId)
            crList.append(rtl.getStr())
        return crList

    def _isAllSame(self, crList):
        flag = crList[0]
        for cr in crList:
            if flag != cr:
                return False
        return True

    def _updateCR(self, itemId, cr):
        #Update the finial summary result table
        self.task.db.cateSummary.insertResult([itemId, cr])
        #Write back into TFIDF result table
        skipList = ['new','manual']
        if cr not in skipList:
            self.task.db.cateTFIDF.updateCR([itemId, cr])
            #We still need to sync with TRD
            action = UpdateTRD(self.task)
            action.execute(itemId, cr)
        pass

    def _isNewMoreThanHalf(self, crList):
        newCrCount = 0
        for cr in crList:
            if cr == 'new':
                newCrCount += 1.0
        if newCrCount/len(crList) > 0.5:
            return True
        else:
            return False

    def _findMaxSameCr(self, crList):
        crDict = {}
        for cr in crList:
            if crDict.has_key(cr):
                crDict[cr] += 1
            else:
                crDict[cr] = 1
        maxPair = (0, 0)
        for cr,count in crDict.items():
            if maxPair[1] < count:
                maxPair = (cr, count)
            elif maxPair[1] == count:
                if maxPair[0] == 'new':
                    maxPair = (cr, count)
        return maxPair

    def _isSameCRMoreThanHalf(self, crList):
        maxInfo = self._findMaxSameCr(crList)
        if maxInfo[1] >= len(crList)/2.0:
            return maxInfo[0]
        else:
            return False

    def _ispartlySameWithMostTFIDF(self, itemIdList, crList):
        tfidfCrList = []
        for itemId in itemIdList:
            rtl = self.task.db.cateSummary.searchTFIDFCR(itemId)
            tfidfCrList.append(rtl.getStr())
        maxInfo = self._findMaxSameCr(tfidfCrList)
        if maxInfo[0] in crList:
            return maxInfo[0]
        else:
            return False
    pass
