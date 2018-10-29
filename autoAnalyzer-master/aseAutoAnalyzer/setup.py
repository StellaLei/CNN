from common.setup import Setup
import common.basicApi as basicApi
from actions.mail import SetupFailReport
import time
import re
import os
import glob
import pdb

class AseSetup(Setup):
    def __init__(self):
        basicApi.d_print('AseSetup: __init__()')
        self.err = []
        self.tcfList = []
        self.jnlPair = []
        self.testSetWorkDir = ''
        self.resultDir = ''
        #Used to store execOut data
        self.execResultDict = {}
        #Used to store current Tcf full name
        self.tcfFullName = ''

    def setupTask(self):
        #1, Collect test case related information, like testTag, testPlatform, testBranch, testSet, etc
        #2, The jnl/log path which we need to read
        #3, Path/file availability check
        basicApi.d_print('AseSetup: setupTask()')
        argList = self.task.argList
        workDir = argList[0]
        testSet = argList[1]
        tag = argList[2]
        user = argList[3]
        platform = '%s,%s'%(argList[4], argList[5])
        lockSch = argList[6]
        pageSize = argList[7]
        branch = argList[8]
        tagTime = basicApi.parseDate(argList[9])
        #init task
        self.task.workDir = workDir
        self.task.testSet = testSet
        self.task.tag = tag
        self.task.user = user
        self.task.platform = platform
        self.task.branch = branch
        self.task.tagTime = tagTime
        #Get each tcf storage path
        argList = [workDir, testSet, lockSch, pageSize]
        self.tcfList = self._findTcfsBySet(argList)
        #Generate auto-analyzer log directory
        self.aaLogDir = os.path.join(self.testSetWorkDir, 'autoAnalyzer')
        if os.path.exists(self.aaLogDir):
            basicApi.deleteDir(self.aaLogDir)
            time.sleep(3)
        os.mkdir(self.aaLogDir)
        #Stroe this path into task object
        self.task.aaLogDir = self.aaLogDir
        #Collect *.tcf and *.exec file pairs
        if self.tcfList:
            for tcf in self.tcfList:
                execOutFileList = glob.glob('%s/exec.out.*'%tcf)
                jnlFileList = glob.glob('%s/journal.exec.*'%tcf)
                for index in range(len(execOutFileList)):
                    execOut = execOutFileList[index]
                    jnl = jnlFileList[index]
                    self.jnlPair.append((jnl, execOut))


    def _findTcfsBySet(self, argList):
        workDir,testSet,lockSch,pageSize = argList
        if not os.path.exists(workDir):
            self.err.append('Can not find folder under %s\n'%workDir)
            return False
        destDir = os.path.join(workDir,'%s__%s_%s_*'%(testSet,lockSch,pageSize))
        testSetList = glob.glob(destDir)
        if testSetList == []:
            self.err.append('No file/folder under %s\n'%workDir)
            return False
        latestDir = basicApi.getLatestDir(testSetList)
        self.testSetWorkDir = latestDir
        if not os.path.exists(latestDir):
            self.err.append('Can not find newest folder under %s\n'%latestDir)
            return False
        #Check whether test set directory is empty
        dirIter = os.walk(self.testSetWorkDir)
        dirInfo = dirIter.next()
        if len(dirInfo[1]) + len(dirInfo[2]) == 0:
            #skip to analysis this directory
            raise basicApi.PROCESS_ERROR('Test set is empty, it maybe due to grid re-run action!')
        resultDir = os.path.join(latestDir, 'result.%s'%testSet)
        self.resultDir = resultDir
        if not os.path.exists(resultDir):
            self.err.append('Can not find path: %s\n'%resultDir)
            return False
        tcfList = self._getAllTcfs(resultDir)
        if tcfList == []:
            self.err.append('Test case inital failed, no TCF run result under this folder:\n\t%s\n'%resultDir)
            return False
        else:
            return tcfList

    def _getAllTcfs(self, workDir):
        rtl = []
        for subDir in glob.glob('%s/*'%workDir):
            if os.path.isdir(subDir):
                rtl.append(subDir)
        return rtl



    def checkTaskEnv(self):
        #1, Does testing framework in normal status
        #2, Does test case running currectly
        basicApi.d_print('AseSetup: checkTaskEnv()')
        if not self.tcfList:
            #Check whether each test case has been finished normally
            #Check whether quasr setup successfully
            #os.chmod(autoAnalyzerDir, 0766)
            #Write setup failed data into database
            self.task.db.cateSummary.insertSetupFail([self.task.tag,
                                                      self.task.tagTime,
                                                      self.task.branch,
                                                      self.task.platform,
                                                      self.task.testSet,
                                                      self.task.workDir,
                                                      self.task.user,
                                                      '?'])
            basicApi.writeFile(os.path.join(self.aaLogDir, 'autoAnalysis.err'), self.err)
            #Send mail to BianHong for Quasr setup fail
            sfr = SetupFailReport(self.task)
            sfr.execute(self.resultDir)
            #Raise exception
            raise basicApi.PROCESS_ERROR('Quasr test case setup failed!')
        
        pass

    def parpareTaskData(self):
        #1, Split whole jnl file into case blocks
        #2, Save each blocks into local disk
        #3, Write caseName to jnl maps into task object
        #caseList = [(itemId, caseName), ...]
        basicApi.d_print('AseSetup: parpareTaskData()')
        for jnlPath,execPath in self.jnlPair:
            self._fillExecOutDic(execPath)
            for jnlCaseNum,block in self._jnlGenerator(jnlPath):
                caseName = self._getCaseName(jnlCaseNum)
                #Insert current failed test case information into DB
                rtl = self.task.db.cateCycleInfo.insertItems([self.task.tag,
                                                              self.task.tagTime,
                                                              self.task.branch,
                                                              self.task.platform,
                                                              self.task.testSet,
                                                              caseName,
                                                              self.task.workDir,
                                                              self.task.user,
                                                              '?'])
                #Get return itemId from DB
                itemId = rtl.getProcRtId()
                #Wrtie block data into disk with itemId
                basicApi.writeFile(self.task.getJnlStoreName(itemId), block)
                #Append caseList for current task
                self.task.caseList.append((str(itemId), caseName))
        #Log jnl paser info
        basicApi.writeFile(os.path.join(self.aaLogDir, 'autoAnalysis.log'), self.err)
        pass

    def _execOutGenerator(self, execOutFile):
        fd = basicApi.openFile(execOutFile, "r")
        for line in fd:
            matched = re.match(r"(.*)\{([0-9]*)\}\: (\w+)", line)
            if matched:
                yield matched
        fd.close()

    def _fillExecOutDic(self, execOutFile):
        self.execResultDict = {}
        passFlag = False
        for matched in self._execOutGenerator(execOutFile):
            execOutTcfName = matched.group(1)
            execOutCaseNum = matched.group(2)
            tcfExecStatus = matched.group(3)
            if tcfExecStatus == "FAIL"  or tcfExecStatus == "UNRESOLVED":
                self.tcfFullName = execOutTcfName
                self.execResultDict[execOutCaseNum] = True
            elif tcfExecStatus == "PASS" or tcfExecStatus == "UNTESTED":
                passFlag = True
            else:
                passFlag = False
        ##Check exec.out
        title = 'Analysising: %s'%execOutFile
        if self.execResultDict == {}:
            if passFlag == True:
                self.err.append('%s\nINFO: Test case all PASS, quit analysis.\n\n'%title)
            else:
                self.err.append('%s\nERROR: Parse exec.out file failed.\n\n'%title)
        else:
            self.err.append('%s\n'%title)
            for var in self.execResultDict.keys():
                caseName = self._getCaseName(var)
                self.err.append('Fail case: %s\n'%caseName)
            self.err.append('\n\n')

    def _jnlGenerator(self, jnlFile):
        jnlCaseNum = ''
        block = []
        caseNameMatched = False
        fd = basicApi.openFile(jnlFile, 'r')
        for line in fd:
            #check for block saving begin
            matched = re.match(r"^400\|[0-9]+\s+([0-9]+)\s+[0-9]+\s+[0-9:]+\s+[0-9]+\|IC Start", line)
            if matched:
                if self.execResultDict.has_key(matched.group(1)):
                    jnlCaseNum = matched.group(1)
                else:
                    jnlCaseNum = ''
                block = []
            #append test case jounal in block
            if jnlCaseNum != '':
                if line.find(self.tcfFullName) is not -1:
                    caseNameMatched = True
                block.append(line)
                #We just need to check for block saving end in append mode.
                matched = re.match(r"^410\|[0-9]+\s+([0-9]+)\s+[0-9]+\s+[0-9:]+\s+[0-9]+\|IC End", line)
                if matched:
                    if caseNameMatched:
                        yield jnlCaseNum,block
                    jnlCaseNum = ''
                    caseNameMatched = False
        fd.close()

    def _getCaseName(self, caseNum):
        return self.tcfFullName + '{' + caseNum + '}'
