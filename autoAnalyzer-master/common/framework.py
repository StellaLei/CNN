import common.basicApi as basicApi

class Framework(object):
    def __init__(self, clsList):
        basicApi.d_print('common.Framework:__init__()')
        self.clsNameList = []
        for cls in clsList:
           setattr(self, cls.name, cls())
           self.clsNameList.append(cls.name)
        pass

    def run(self, task):
        basicApi.d_print('common.Framework:run()')
        for insName in self.clsNameList:
            instance = getattr(self, insName)
            instance.run(task)
        pass
