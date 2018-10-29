from common.dbAccess import DbCategory
from common.dbAccess import DbAccess
import common.basicApi as basicApi
import sys
#Hana database driver path
sys.path.append('/remote/asepw_archive2/grid/autoAnalyzer/hanaClient')
import hdbcli.dbapi as hanadbapi
#ASE database driver path
#ASE drive need extra ENV variable [SYBASE] and [LD_LIBRARY_PATH] support
#sys.path.append('/remote/asepw_archive2/grid/autoAnalyzer/aseClient')
#import asecli.dbapi as asedbapi

import pdb


class dataSet(object):
    def __init__(self, rtList):
        basicApi.d_print('dataSet:__init__()')
        #Tranlate db return data into an object
        self.args = rtList

    def isEmpty(self):
        if self.args == []:
            return True
        else:
            return False

    def getUnchangable(self):
        return self.args

    def getProcRtId(self):
        return self.args[-1]

    def getStr(self):
        return self.args[0][0]

    def getList(self):
        rtlList = []
        for val in self.args:
            rtlList.append(val[0])
        return rtlList

    def getTuple(self):
        return self.args[0]

    def getDict(self):
        rtlDict = {}
        for key,val in self.args:
            rtlDict[key] = val
        return rtlDict

    def getCluster(self):
        rtlDict = {}
        for key,val in self.args:
            if rtlDict.has_key(key):
                rtlDict[key].append(val)
            else:
                rtlDict[key] = [val]
        return rtlDict


class AseAccess(DbAccess):
    def __init__(self):
        #ASE database driver path
        #ASE drive need extra ENV variable [SYBASE] and [LD_LIBRARY_PATH] support
        sys.path.append('/remote/asepw_archive2/grid/autoAnalyzer/aseClient')
        import asecli.dbapi as asedbapi
        #Begin inital
        self.conn = asedbapi.connect(user='tamqa',
                                     password='only4qa',
                                     servername='qtsServer')
        self.cur = self.conn.cursor()
        #specify QTS schema
        self.cur.execute('use qts_db')

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def searchClosedCR(self, cr, branchName=None):
        if branchName is None:
            sql = "select res_status from resolution_search_vu where bug_id = %s" % cr
        else:
            sql = "select res_status from resolution_search_vu where bug_id = %s and branch = '%s'" % (cr, branchName)
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return dataSet(result)


class HanaAccess(DbAccess):
    def __init__(self):
        basicApi.d_print('HanaDbAccess: __init__()')
        #Initial connection to database
        self.conn = hanadbapi.connect( address  = "lsvxc0035.sjc.sap.corp",
                                   port     = 30015,
                                   user     = "SYSTEM",
                                   password = "Sybase123")
        self.cur = self.conn.cursor()
        #Specify schema name and db path
        self.schema = 'AUTO_ANALYZER'
        self.basePath = 'aseAutoAnalyzer.db'
        #Initial call db access method
        self.cateCycleInfo = CycleInfo(self, 'cycleInfo')
        self.cateTFIDF = TFIDF(self, 'tfidf')
        self.cateCNN = CNN(self, 'cnn')
        self.cateSummary = Summary(self, 'summary')

    def __del__(self):
        self.cur.close()
        self.conn.close()


class CycleInfo(DbCategory):
    def insertItems(self, args):
        result = self.callProc('P_INS_ITEM', tuple(args))
        return dataSet(result)

    def updateTestSetAssignment(self, args):
        result = self.callProc('P_UPD_TESTSET_ASSIGN', tuple(args))
        return dataSet(result)

    def searchItemInfo(self, itemId):
        sql = 'select TAG,PLATFORM,TESTCASE from "AUTO_ANALYZER"."aseAutoAnalyzer.db.cycleInfo.views::V_ITEMS" where ID = %s' % itemId
        result = self.execute(sql)
        return dataSet(result)


class TFIDF(DbCategory):
    def searchFeatureKey_tb(self):
        sql = 'select WORD, WEIGHT from "AUTO_ANALYZER"."aseAutoAnalyzer.db.tfidf.tables::T_FEATURE_KEY"'
        result = self.execute(sql)
        return dataSet(result)

    def insertFeatureKey(self, args):
        result = self.callProc('P_INS_FEATUREKEY', tuple(args))
        return dataSet(result)

    def truncFeatureKey(self):
        result = self.callProc('P_TRC_FEATUREKEY')
        return dataSet(result)

    def insertNotAnalysis(self, args):
        result = self.callProc('P_INS_TFIDF_EMPTY_VEC', tuple(args))
        return dataSet(result)

    def insertTfidfResult(self, args):
        result = self.callProc('P_INS_TFIDF_RESULT', tuple(args))
        return dataSet(result)
   
    def searchAllVecs(self, itemId):
        sql = 'select ID,VECTOR from "AUTO_ANALYZER"."aseAutoAnalyzer.db.tfidf.tables::T_MSG" where ID != %s'%itemId
        result = self.execute(sql)
        return dataSet(result)

    def insertSimilarity(self, args):
        result = self.callProc('P_INS_FAIL_SIM', tuple(args))
        return dataSet(result)

    def updateCR(self, args):
        result = self.callProc('P_UPD_CR', tuple(args))
        return dataSet(result)

    def truncMsgVector(self):
        result = self.callProc('P_TRC_VECTOR')
        return dataSet(result)

    def updateMsgVector(self, args):
        result = self.callProc('P_UPD_VECTOR', tuple(args))
        return dataSet(result)

    def cleanEmptyVector(self):
        result = self.callProc('P_CLN_VECTOR')
        return dataSet(result)


class CNN(DbCategory):
    def searchItemIdList(self):
        sql = 'select ITEM_ID from "AUTO_ANALYZER"."aseAutoAnalyzer.db.cnn.tables::T_RESULT"'
        result = self.execute(sql)
        return dataSet(result)

    def insertResult(self, args):
        result = self.callProc('P_INS_CNN_RESULT', tuple(args))
        return dataSet(result)

    def updateCNNModel(self, args):
        result = self.callProc('P_UPD_CNN_MODEL', tuple(args))
        self.db.conn.commit()
        return dataSet(result)

    def searchCNNModel(self):
        sql = 'select MODEL from "AUTO_ANALYZER"."aseAutoAnalyzer.db.cnn.tables::T_CNN_MODEL" where MODEL is not NULL'
        result = self.execute(sql)
        return dataSet(result)

    def searchCrItemPair(self):
        sql = '''select CR, ID from "AUTO_ANALYZER"."aseAutoAnalyzer.db.summary.views::V_RESULT" where CR != 'new' '''
        result = self.execute(sql)
        return dataSet(result)


class Summary(DbCategory):
    def insertSetupFail(self, args):
        result = self.callProc('P_INS_SETUP_FAIL', tuple(args))
        return dataSet(result)

    def insertResult(self, args):
        result = self.callProc('P_INS_RESULT', tuple(args))
        return dataSet(result)

    def insertRecalculateLog(self):
        result = self.callProc('P_INS_RECALCULATE')
        return dataSet(result)

    def updateCluster(self, args):
        #Need input test set name
        result = self.callProc('P_UPD_CLUSTER', tuple(args))
        return dataSet(result)

    def updateCR(self, args):
        result = self.callProc('P_UPD_CR', tuple(args))
        return dataSet(result)

    def removeItem(self, args):
        result = self.callProc('P_DEL_ITEM', tuple(args))
        return dataSet(result)

    def removeClosedCR(self, args):
        result = self.callProc('P_CLN_CLOSED_CR', tuple(args))
        return dataSet(result)

    def searchClusterIdByItemId(self, itemId):
        sql = 'select ID from "AUTO_ANALYZER"."aseAutoAnalyzer.db.summary.tables::T_CLUSTER" where ITEM_ID = %s'%itemId
        result = self.execute(sql)
        return dataSet(result)

    def searchItemsByClusterId(self, clusterId):
        sql = 'select ITEM_ID from "AUTO_ANALYZER"."aseAutoAnalyzer.db.summary.tables::T_CLUSTER" where ID = %s'%clusterId
        result = self.execute(sql)
        return dataSet(result)

    def searchCNNResult(self, args):
        sql = '''select ID, CR from "AUTO_ANALYZER"."aseAutoAnalyzer.db.cnn.views::V_RESULT"
                 where TAG = '%s' and PLATFORM = '%s' and BRANCH = '%s' and TESTSET = '%s' and TAGTIME = '%s'
              ''' % (args[0], args[1], args[2], args[3], args[4])
        result = self.execute(sql)
        return dataSet(result)

    def searchAutoAnalysisSummary(self, args):
        sql = '''select ID,TESTCASE,CR,USR  from "AUTO_ANALYZER"."aseAutoAnalyzer.db.summary.views::V_RESULT"
                 where TAG = '%s' and PLATFORM = '%s' and BRANCH = '%s' and TESTSET = '%s' and TAGTIME = '%s' order by CR desc
              ''' % (args[0], args[1], args[2], args[3], args[4])
        result = self.execute(sql)
        return dataSet(result)

    def searchTestSet(self, tag):
        sql = '''select distinct TAG, PLATFORM, BRANCH, TESTSET, WORKDIR, USR from "AUTO_ANALYZER"."aseAutoAnalyzer.db.summary.views::V_RESULT"
                 where TAG = '%s' ''' % tag
        result = self.execute(sql)
        return dataSet(result)

    def searchCNNcrByItemId(self, itemId):
        sql = 'select CR from "AUTO_ANALYZER"."aseAutoAnalyzer.db.cnn.views::V_RESULT" where ID = %s'%(itemId)
        result = self.execute(sql)
        return dataSet(result)

    def searchTFIDFCR(self, itemId):
        sql = 'select CR from "AUTO_ANALYZER"."aseAutoAnalyzer.db.tfidf.views::V_RESULT" where ID = %s'%(itemId)
        result = self.execute(sql)
        return dataSet(result)

    def searchCleanCandidate(self):
        sql = '''select ID,TAG,BRANCH,PLATFORM,TESTSET,TESTCASE,CR from "AUTO_ANALYZER"."aseAutoAnalyzer.db.summary.views::V_RESULT"'''
        result = self.execute(sql)
        return dataSet(result)

    def searchDistinctCR(self):
        sql = '''select distinct BRANCH,CR from "AUTO_ANALYZER"."aseAutoAnalyzer.db.summary.views::V_RESULT" \
                 where CR != 'new' and CR != 'manual' '''
        result = self.execute(sql)
        return dataSet(result)

    def searchItem(self, cr):
        sql = '''select ID from "AUTO_ANALYZER"."aseAutoAnalyzer.db.summary.views::V_RESULT" where CR = '%s' ''' % cr
        result = self.execute(sql)
        return dataSet(result)
   
