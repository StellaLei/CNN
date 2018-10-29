#This is another Singleton model, achieve with decorator
def singleton(cls):
    instances = []
    def getinstance(*args, **kwargs):
        if not instances:
            instances.append(cls(*args, **kwargs))
        return instances[0]
    return getinstance
