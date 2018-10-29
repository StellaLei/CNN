from common.analysis import Analysis
import common.basicApi as basicApi
from aseAutoAnalyzer.TFIDF.analyzer import TFIDF
from aseAutoAnalyzer.CNN.analyzer import CNN
from common.environment import Env

class AseAnalysis(Analysis):
    def __init__(self):
        basicApi.d_print('AseAnalysis: __init__()')
        self.tfidf = TFIDF()
        self.cnn = CNN()
        pass

    def run(self, task):
        basicApi.d_print('AseAnalysis: run()')
        self.cnn.run(task)
        self.tfidf.run(task)
        pass

    def updateModel(self, task):
        if Env().homeDir == '/remote/asepw_archive2/grid/autoAnalyzer/gitAutoAnalyze':
            #This is used for re-calculation
            basicApi.d_print('AseAnalysis: updateModel()')
            #Record recalculation action into db
            task.db.cateSummary.insertRecalculateLog()
            #Begin update
            self.cnn.update(task)
            self.tfidf.update(task)
        else:
            print('Re-calculate must be run under:')
            print('    /remote/asepw_archive2/grid/autoAnalyzer/gitAutoAnalyze')
        pass
    pass
