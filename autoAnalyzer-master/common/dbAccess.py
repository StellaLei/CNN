import common.basicApi as basicApi

class DbAccess(object):
    def __init__(self):
        basicApi.d_print('common.DbAccess:__init__()')
        pass

class DbCategory(object):
    def __init__(self, db, categoryName):
        basicApi.d_print('common.DbCategory:__init__()')
        self.db = db
        self.name = categoryName

    def callProc(self, proc, args=()):
        basicApi.d_print('common.DbCategory:callProc()')
        sProc = '"%s"."%s.%s.procs::%s"'%(self.db.schema, self.db.basePath, self.name, proc)
        #print('%s'%(sProc))
        #print(tuple(args))
        return self.db.cur.callproc(sProc, tuple(args))
        #return self.db.cur.fetchall()

    def execute(self, sql):
        basicApi.d_print('common.DbCategory:execute()')
        self.db.cur.execute(sql)
        return self.db.cur.fetchall()
