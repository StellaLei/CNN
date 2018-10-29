import re
import glob
import common.basicApi as basicApi
import pdb

class TestPlanPaser(object):
    def __init__(self):
        self.count = 0
        pass

    def setWorkdir(self, workDir):
        self.workDir = workDir

    def parse(self, testPlan):
        for line in basicApi.readFile(testPlan):
            self.checkTime(line)
            self.checkTag(line)
            self.checkBranch(line)
            self.checkPlatform(line)
            self.printTestSet(line)

    def checkTime(self, line):
        matched = re.match(r"Start Date:\s+(\S+).*", line)
        if matched:
            self.time = matched.group(1)
            #print('Time = %s' % self.time)

    def checkTag(self, line):
        matched = re.match(r"Cycle Tag:\s+(\S+).*", line)
        if matched:
            self.tag = matched.group(1)
            #print('Tag = %s' % self.time)


    def checkBranch(self, line):
        matched = re.match(r"Branch for Reporting:\s+(\S+).*", line)
        if matched:
            self.branch = matched.group(1)
            #print('Branch = %s' % self.time)

    def checkPlatform(self, line):
        matched = re.match(r"Platform:\s+(.*),(.*),(.*),(.*),(.*)", line)
        if matched:
            self.platform = matched.group(1)
            self.bit = matched.group(2)
            self.lock = matched.group(3)
            self.pagesize = matched.group(4)
            self.svrtype = matched.group(5)
            #print('Result = %s, %s, %s, %s, %s' % (self.platform, self.bit, self.lock, self.pagesize, self.svrtype))

    def printTestSet(self, line):
        #pdb.set_trace()
        matched = re.match(r"(\S+)\s+##\s+(\S+)\s+.*", line)
        if matched:
            self.testset = matched.group(1)
            self.user = matched.group(2)
            print('echo "current test set: %s"' % self.testset)
            print('python /remote/asepw_archive2/grid/autoAnalyzer/gitAutoAnalyze/main.py %s %s %s %s %s %s %s %s %s %s' 
            % (self.workDir, self.testset, self.tag, self.user, self.platform, self.bit, self.lock, self.pagesize, self.branch, self.time))
            self.count += 1





if __name__ == '__main__':
    platformList = glob.glob('/remote/asepw_archive1/grid/project/fanf_SP03_PLx_PW_lam')
    print('#!/usr/bin/sh')
    print('\n')
    for platform in platformList:
        runList = glob.glob('%s/func.lam.demo/workdir/run_*' % platform)
        runPath = basicApi.getLatestDir(runList)
        #print(runPath)
        print('echo "Begin analysis: %s"' % runPath)
        #print('%s/Templates/plan.txt' % platform)
        tpp = TestPlanPaser()
        tpp.setWorkdir(runPath)
        tpp.parse('%s/Templates/plan.txt' % platform)
        #print tpp.count
