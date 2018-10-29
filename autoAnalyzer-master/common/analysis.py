import common.basicApi as basicApi

class Analysis(object):
    name = 'Analysis'
    def __init__(self):
        basicApi.d_print('common.Analysis: __init__()')
        pass
    def run(self, task):
        basicApi.d_print('common.Analysis: run()')
        pass
    pass
