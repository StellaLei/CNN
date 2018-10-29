import pdb

class UploadCNNModel(object):
    def __init__(self, task):
        self.task = task
        pass

    def execute(self, tarBall):
        #Read file
        with open(tarBall, 'rb') as fd:
            binaryData = fd.read()
        hexData= binaryData.encode('hex')
        #upload runs.tar into database
        self.task.db.cateCNN.updateCNNModel([hexData])
        pass

    def getCrItemPairs(self):
        rtl = self.task.db.cateCNN.searchCrItemPair()
        return rtl.getUnchangable()
        pass
    pass
