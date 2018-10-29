import common.basicApi as basicApi

class Setup(object):
    name = 'Setup'
    def __init__(self):
        basicApi.d_print('common.Setup:__init__()')
        pass

    def run(self, task):
        basicApi.d_print('common.Setup:run()')
        self.task = task
        self.setupTask()
        self.checkTaskEnv()
        self.parpareTaskData()

    def setupTask(self):
        #1, Collect test case related information, like testTag, testPlatform, testBranch, testSet, etc
        #2, The jnl/log path which we need to read
        #3, Path/file availability check
        basicApi.d_print('common.Setup:setupTask()')
        pass

    def checkTaskEnv(self):
        #1, Does testing framework in normal status
        #2, Does test case running currectly
        basicApi.d_print('common.Setup:checkTaskEnv()')
        pass

    def parpareTaskData(self):
        #1, Split whole jnl file into case blocks
        #2, Save each blocks into local disk
        #3, Write caseName to jnl maps into task object
        basicApi.d_print('common.Setup:parpareTaskData()')
        pass

