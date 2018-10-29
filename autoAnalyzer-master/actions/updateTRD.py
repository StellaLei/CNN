import common.basicApi as basicApi
import pdb

#Update specific CR to TRD
class UpdateTRD(object):
    def __init__(self, task):
        basicApi.d_print('UpdateTRD:__init__()')
        self.task = task
        pass

    def execute(self, itemId, cr):
        basicApi.d_print('UpdateTRD:execute()')
        #Get needed information from database
        rtl = self.task.db.cateCycleInfo.searchItemInfo(itemId)
        (tag, platformBit, fullCaseName) = rtl.getTuple()
        #sync test case attached CR from our data base to TRD
        pathList = fullCaseName.split('/')
        caseName = pathList[-1]
        cmd = '/remote/quasr1/quasr/nightly/build/linux/bin/quasr_trd add cr -case_name "%s" \
               -tag %s -number %s -plat_and_bit %s' % (caseName, tag, cr, platformBit)
        return basicApi.quasrCmd(cmd)
        pass

    def deleteTRD(self, itemId, cr):
        basicApi.d_print('UpdateTRD:deleteTRD()')
        rtl = self.task.db.cateCycleInfo.searchItemInfo(itemId)
        (tag, platformBit, fullCaseName) = rtl.getTuple()  
        #sync test case attached CR from our data base to TRD
        pathList = fullCaseName.split('/')
        caseName = pathList[-1]
        cmd = '/remote/quasr1/quasr/nightly/build/linux/bin/quasr_trd delete cr -case_name "%s" \
               -tag %s -number %s -plat_and_bit %s' % (caseName, tag, cr, platformBit)
        return basicApi.quasrCmd(cmd)
        pass
 
    pass
