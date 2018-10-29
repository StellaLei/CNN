import common.basicApi as basicApi

class ReAssignUsr(object):
    def __init__(self, task):
        basicApi.d_print('ReAssignUsr:__init__()')
        self.task = task
        pass

    def execute(self, assignDict):
        basicApi.d_print('ReAssignUsr:execute()')
        for testSet, userName in assignDict.items():
            print('test_set: %s to user: %s'%(testSet, userName))
            self.task.db.cateCycleInfo.updateTestSetAssignment([testSet, usrName])
        pass
    pass
