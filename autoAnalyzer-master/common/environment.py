from common.singleton import singleton
import common.basicApi as basicApi
import yaml
import os

@singleton
class Env(object):
    name = 'Env'
    def __init__(self):
        basicApi.d_print('common.Env:__init__()')
        self.homeDir = os.environ['PYTHONPATH']
        self.configDict = {}
        self._loadConfig('%s/config.yml' % self.homeDir)

    def _loadConfig(self, fileName):
        basicApi.d_print('common.Env:_loadConfig()')
        fd = file(fileName, 'r')
        cfgDict = yaml.load(fd)
        #Process absolute path
        for key,value in cfgDict['ABSOLUTE_PATH'].items():
            self.configDict[key] = value
        #Process relative path
        for key,value in cfgDict['RELATIVE_PATH'].items():
            self.configDict[key] = '%s/%s' % (self.homeDir ,value)
        pass

    def getPath(self, key):
        basicApi.d_print('common.Env:getPath()')
        return self.configDict[key]
