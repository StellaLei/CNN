import common.basicApi as basicApi

class Analyzer(object):
    name = 'Analyzer'
    def __init__(self):
        basicApi.d_print('common.Analyzer:__init__()')
        pass

    def run(self, task):
        basicApi.d_print('common.Analyzer:run()')
        #self.task = task
        self.setTask(task)
        self.preProcess()
        self.analysing()
        self.record()

    def preProcess(self):
        #1, Define your own filter to make jnl block simple.
        #2, For TF/IDF to make jnl into vector here.
        #3, For CNN load learning mode here.
        basicApi.d_print('common.Analyzer:preProcess()')
        pass

    def analysing(self):
        #1, Run analyzer method:
        #   TF/IDF : decision tree
        #   CNN    : Learning model
        basicApi.d_print('common.Analyzer:analysing()')
        pass

    def record(self):
        #1, Write data into DB
        basicApi.d_print('common.Analyzer:record()')
        pass

    def setTask(self, task):
        basicApi.d_print('common.Analyzer:setTask()')
        self.task = task
        pass
