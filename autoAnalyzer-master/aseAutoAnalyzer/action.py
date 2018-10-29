import common.basicApi as basicApi
from common.action import Action
from aseAutoAnalyzer.task import AseTask
from actions.reCalculateModel import ReCalculateModel
from actions.uploadCNNModel import UploadCNNModel
from actions.manualUpdateItem import ManualUpdateItem
from actions.manualRemoveItem import ManualRemoveItem
from actions.updateTRD import UpdateTRD
from actions.cycleCleanUp import CycleCleanUp
from actions.mail import TestsetReport
from common.environment import Env
import pdb


class AseAction(Action):
    def __init__(self):
        basicApi.d_print('AseAction:__init__()')
        self.task = AseTask()
        pass

    def sendMailSetSummary(self, tag):
        tsr = TestsetReport(self.task)
        #Search testset summary with tag
        rtl = self.task.db.cateSummary.searchTestSet(tag)
        testsetList = rtl.getUnchangable()
        #iterate each item
        for row in testsetList:
            self.task.tag = row[0]
            self.task.platform = row[1]
            self.task.branch = row[2]
            self.task.testSet = row[3]
            self.task.workDir = row[4]
            self.task.user = row[5]
            self.task.aaLogDir = '%s/autoAnalyzer' % Env().getPath('TEMP_PATH')
            if not basicApi.dirExist(self.task.aaLogDir):
                basicApi.makeDir(self.task.aaLogDir)
            tsr.execute()
        pass
#    def sendMail(self):
#        #1, Send out Mail for current analysis result.
#        print('Summary:endMail')
#        pass

    def reCalculate(self):
        #This function used to re-calculate tfidf vector and re-train CNN model
        # 1, tfidf re-calculate
        # 2, CNN model re-train
        rec = ReCalculateModel(self.task)
        rec.execute()
        pass

    def reAssignUsr(self, assignment):
        rsu = ReAssignUsr(self.task)
        rsu.execute(assignment)
        pass

    def updateItem(self, itemId, cr):
        #Manually update CR
        udi = ManualUpdateItem(self.task)
        udi.execute(itemId, cr)
        pass

    def deleteItem(self, itemId):
        #Delete fake error item
        dli = ManualRemoveItem(self.task)
        dli.execute(itemId)
        pass

    def removeCR(self, cr):
        #Remove the specific CR and related items
        dli = ManualRemoveItem(self.task)
        dli.deleteCR(cr)
        pass
    def updTRD(self, itemId, cr):
        sct = UpdateTRD(self.task)
        sct.execute(itemId, cr)
        pass

    def cleanUp(self):
        #Sync result from TRD and clean closed CR
        ccu = CycleCleanUp(self.task)
        ccu.execute()

    def uploadCNN(self, fileName):
        #Just used for Mayu to upload CNN model
        ulc = UploadCNNModel(self.task)
        ulc.execute(fileName)

    def getCrItemIdPair(self):
        #Just used for Mayu to upload CNN model
        ulc = UploadCNNModel(self.task)
        return ulc.getCrItemPairs()
    pass
