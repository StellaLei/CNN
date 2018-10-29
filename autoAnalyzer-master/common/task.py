from common.dbAccess import DbAccess
import common.basicApi as basicApi


class Task(object):
    def __init__(self, db=DbAccess, analyzers=[]):
        basicApi.d_print('common.Task:__init__()')
        self.db = db()
        self.analyzers = analyzers
        pass

    def execute(self):
        basicApi.d_print('common.Task:__execute__()')
        pass
