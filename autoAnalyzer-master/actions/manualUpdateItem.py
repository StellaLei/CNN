import common.basicApi as basicApi
from actions.updateTRD import UpdateTRD


class ManualUpdateItem(object):
    def __init__(self, task):
        basicApi.d_print('ManualUpdateItem:__init__()')
        self.task = task
        self.udt = UpdateTRD(task)
        pass

    def execute(self, itemId, cr):
        basicApi.d_print('ManualUpdateItem:execute()')
        #Update user specified CR into database
        self.updateDB(itemId, cr)
        #We still need update this CR in TRD
        self.updateTRD(itemId, cr)
        pass

    def updateDB(self, itemId, cr):
        # Update CR status into database
        self.task.db.cateSummary.updateCR([itemId, cr])
        # Backwords sync with TFIDF result table
        self.task.db.cateTFIDF.updateCR([itemId, cr])
        pass

    def updateTRD(self, itemId, cr):
        #Write user specified cr into TRD
        self.udt.execute(itemId, cr)
        pass
    pass
