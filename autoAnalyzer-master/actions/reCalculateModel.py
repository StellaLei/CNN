from aseAutoAnalyzer.analysis import AseAnalysis

class ReCalculateModel(object):
    def __init__(self, task):
        self.task = task
        pass

    def execute(self):
        analysis = AseAnalysis()
        analysis.updateModel(self.task)
        pass
