import common.basicApi as basicApi
from actions.updateTRD import UpdateTRD
from actions.manualRemoveItem import ManualRemoveItem
from actions.manualUpdateItem import ManualUpdateItem
from aseAutoAnalyzer.dbAccess import AseAccess
import os,re
import pdb


class CycleCleanUp(object):
    def __init__(self, task):
        basicApi.d_print('CycleCleanUp:__init__()')
        self.task = task
        #initial update and remove actions
        self.mri = ManualRemoveItem(task)
        self.mui = ManualUpdateItem(task)
        self.upt = UpdateTRD(task)
        self.qtsdb = AseAccess()
        # Setup Quasr_trd executing PATH
        self._setEnv()

    def execute(self):
        basicApi.d_print('CycleCleanUp:execute()')
        #Infact there are 2 jobs:
        #1, Check all not processed items in current cycle, sync the data with TRD.
        #2, Check all CR status, remove closed CR related items.
        print('****************************************')
        print('     Sync analysis result from TRD:     ')
        print('****************************************')
        self.syncFromTRD()
        print('\n')
        print('****************************************')
        print('   Check CR status on current branch:   ')
        print('****************************************')
        self.removeCloseCR()

    def removeCloseCR(self):
        #Find closed CR candidate
        rtl = self.task.db.cateSummary.searchDistinctCR()
        bcList = rtl.getUnchangable()
        for branch,cr in bcList:
            rtl = self.qtsdb.searchClosedCR(cr,branch)
            stat = rtl.getList()
            #print('CR status: %s'%stat)
            if len(stat) >= 1:
                #There are resolution on current branch.
                rtl = self.qtsdb.searchClosedCR(cr)
                statList = rtl.getList()
                #check whether there are still open resolution
                if 'New' in statList:
                    #Skip to do action
                    continue
                elif 'Open' in statList:
                    #skip to do action
                    continue
                else:
                    #This CR is fully closed
                    #Remove it from database
                    self.task.db.cateSummary.removeClosedCR([cr])
                    print('All resolution closed on the CR:%s. Delete it from DB.' % cr)
            else:
                #Manually work needed
                #Run to here means there is no resolution for current branch
                print('CR:%s has NO resolution for branch %s, please open it!' % (cr, branch))

    def syncFromTRD(self):
        #When sync from TRD in fact, we did 2 things:
        #1, Find Cr number from TRD and update it to our database
        #2, If test case does not exist in TRD, we will update TRD
        rtl = self.task.db.cateSummary.searchCleanCandidate()
        candidateList = rtl.getUnchangable()
        #Begin checking
        for itemId,tagName,branchName,platform,setName,fullCaseName,crNum in candidateList:
            caseName = fullCaseName.split('/')[-1]
            #print "%s,%s,%s"%(itemId,tagName,caseName)
            #As there are still some case not in TRD so we need to pick them up
            (stat, cr) = self._searchTrdHistory(tagName, branchName, platform, setName, caseName)
            if stat == 'suc':
                #As discussed with Mayu, we cannot remove any item data which is attached with a CR.
                #As we donot know whether it is closed.
                #modified by jingyaz, after disscussed with Mayu and Wanghao, we should remove the item if it passed
                self.mri.execute(itemId, crNum)
                print('Test case pass, no cr attached, delete itemId=%s, tag=%s, case=%s'%(itemId, tagName, caseName))
            elif stat == 'updateTrd':
                print('Test case does not exit in TRD, itemId=%s, tag=%s, set=%s, branch=%s, \
                       case=%s ---> auto add in TRD' % (itemId,tagName,setName,branchName,caseName))
            elif cr:
                #Checking this CR whether need sync
                rtl = self.qtsdb.searchClosedCR(cr)
                statList = rtl.getList()
                #check whether there are still open resolution
                #print('itemid=%s,cr=%s' % (itemId, cr))
                if 'New' in statList:
                    #Auto attach CR to test case
                    self.mui.updateDB(itemId, cr)
                    print('Attach cr=%s to itemId=%s, tag=%s, case=%s'%(cr, itemId, tagName, caseName))
                elif 'Open' in statList:
                    #Auto attach CR to test case
                    self.mui.updateDB(itemId, cr)
                    print('Attach cr=%s to itemId=%s, tag=%s, case=%s'%(cr, itemId, tagName, caseName))
                else:
                    #Test case attach CR in TRD, But CR was closed
                    print('CR=%s is closed, skip update itemId=%s, tag=%s, case=%s'%(cr, itemId, tagName, caseName))
            elif stat is None and cr is None:
                print('Error: itemId=%s, tag=%s, case=%s does not running on branch %s.' % (itemId,tagName,caseName,branchName))
            else:
                #Test case still open, call for manual analysis
                print('Case status is %s, but NO cr attach to TRD for itemId=%s, tag=%s, case=%s' % (stat, itemId, tagName, caseName))

    def _searchTrdHistory(self, tagName, branchName, platform, setName, caseName):
        #compose trd command
        trdCmd = 'quasr_trd history -case_name "%s" -tag %s' % (caseName, tagName)
        # Get data from quasr_trd
        trdHistory = basicApi.execCmd(trdCmd)
        if trdHistory == '':
            #quasr_trd command execute failed, update current test case into TRD
            trdCmd = 'quasr_trd add testcase -case_name "%s" -testset_name %s -branch_name %s \
                      -description "Auto add new case."' % (caseName, setName, branchName)
            basicApi.execCmd(trdCmd)
            stat, cr = ('updateTrd', None)
        else:
            # find the latest record which in the same platform
            tmp_trdHistory = self._findTRDHistory(trdHistory, caseName, platform)
            if tmp_trdHistory != None:
                # Extract data from Trd_history
                (stat, cr) = self._findCaseStat(caseName, tmp_trdHistory)
            else:
                stat = None
                cr = None
        if not stat:
            print 'TRD process Failed:'
            print 'Command: %s' % trdCmd
        return (stat, cr)

    def _setEnv(self):
        #Setup QUASR_DRIVER
        quasrDriver = '/remote/quasr1/quasr/nightly/build/linux'
        os.environ['QUASR_DRIVER'] = quasrDriver
        #Setup PATH
        qTrdPath = '%s/bin' % quasrDriver
        path = os.environ['PATH']
        os.environ['PATH'] = '%s:%s' % (qTrdPath, path)

    def is_number(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def _findTRDHistory(slef, trdHis, caseName, platform):
        plat_form = platform.split(',')[0]
        bit = platform.split(',')[1]
        casePattern = r'^%s' % caseName
        casePattern = casePattern.replace('{', '\{')
        casePattern = casePattern.replace('}', '\}')
        for line in trdHis.split('\n'):
            if re.match(casePattern, line):
                itemList = line.split()
                tmp_pltfm = itemList[1]
                tmp_bit = itemList[2] 
                if tmp_pltfm == plat_form and tmp_bit == bit:
                    return line
                else:
                    continue

    def _findCaseStat(self, caseName, trdHis):
        stat = None
        cr = None
        casePattern = r'^%s' % caseName
        casePattern = casePattern.replace('{', '\{')
        casePattern = casePattern.replace('}', '\}')
        for line in trdHis.split('\n'):
            if re.match(casePattern, line):
                # find out case status and attached CR number
                itemList = line.split()
                stat = itemList[6]
                if stat == 'suc':
                    #Item index 9 is the posistion of CR, 
                    #but if there is no CR attached, it 
                    #will use the next position, it maybe the user name
                    #So we use this to distingish whether it is a CR number.
                    if self.is_number(itemList[9]):
                        cr = itemList[9]
                    else:
                        cr = None
                else:
                    #status is fail
                    cr = itemList[9]
                    # CR number should be at No.9
                    # But if not exist, then means no CR has been attached.
                    if not re.match(r'[0-9]+', cr):
                        cr = None
        return (stat, cr)
