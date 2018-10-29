import common.basicApi as basicApi

class Summary(object):
    name = 'Summary'
    def __init__(self):
        basicApi.d_print('common.Summary:__init__()')
        pass

    def run(self, task):
        basicApi.d_print('common.Summary:run()')
        self.task = task
        self.sum()
        #self.sendMail()
        #send mail operation should move to action module

    def sum(self):
        #Read prediction from each DB and merge them together.
        basicApi.d_print('common.Summary:sum()')
        pass
