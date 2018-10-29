import common.basicApi as basicApi
from actions.updateTRD import UpdateTRD

class ManualRemoveItem(object):
    def __init__(self, task):
        basicApi.d_print('ManualRemoveItem:__init__()')
        self.task = task
        self.udt = UpdateTRD(task)
        pass

    def execute(self, itemId, cr):
        basicApi.d_print('ManualRemoveItem:execute()')
        #Remove fake error message items from db
        #self.task.db.cateSummary.removeItem([itemId])
        #Do we need to check whether this itemId has CR attached.
        #If yes, then we need to remove it from TRD when we remove it.
        #after discussed with wanghao, we need to remove it from TRD
        if cr != 'new' and cr != 'manual':
            self.udt.deleteTRD(itemId, cr)
        #Remove fake error message items from db
        self.task.db.cateSummary.removeItem([itemId]) 
        pass

    def deleteCR(self, cr):
        basicApi.d_print('ManualRemoveItem:deleteCR()') 
        rtl = self.task.db.cateSummary.searchItem(cr)
        itemList = rtl.getList() 
        for itemId in itemList:
            self.udt.deleteTRD(itemId, cr)
            self.task.db.cateSummary.removeItem([itemId])
    pass
