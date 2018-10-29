from common.task import Task
from common.environment import Env
from aseAutoAnalyzer.dbAccess import HanaAccess
import common.basicApi as basicApi


class AseTask(Task):
    def __init__(self, db=HanaAccess, analyzers=[]):
        basicApi.d_print('AseTask: __init__()')
        super(AseTask, self).__init__(db, analyzers)
        #Just used for exactly same error message file/attach CR
        self.jnlStorePath = Env().getPath('JNL_STORE_PATH')
        pass

    def initial(self, argList):
        basicApi.d_print('AseTask: initial()')
        self.argList = argList
        #caseList : [(itemId, caseName), ...]
        self.caseList = []

    def getJnlStoreName(self, jnlStoreId):
        #return self.jnlStorePath + 'ErrMsg_' + str(jnlStoreId) + '.jnl'
        return '%s/ErrMsg_%s.jnl'%(self.jnlStorePath, jnlStoreId)

    def getStoreJnlList(self):
        rtList = []
        for itemId,_ in self.caseList:
            rtList.append(self.getJnlStoreName(itemId))
        return rtList

    def getAllStoreJnlList(self):
        jnlPattern = '%s/*.jnl'%self.jnlStorePath
        return basicApi.getFilesUnderDir(jnlPattern)
    pass
