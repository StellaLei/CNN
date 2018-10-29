import common.basicApi as basicApi

class Action(object):
    name = 'Action'
    def __init__(self):
        basicApi.d_print('common.Action:__init__()')
        pass

    def someAction():
        basicApi.d_print('common.Action:someAction()')
        pass
