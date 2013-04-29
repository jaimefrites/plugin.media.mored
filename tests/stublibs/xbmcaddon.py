from collections import defaultdict

class Addon(object):
    _mem = defaultdict(str)

    def __init__(self, name):
        pass

    def getAddonInfo(self, info):
        pass

    def getSetting(self, name):
        val = self._mem[name]
        return val

    def setSetting(self, name, value):
        self._mem[name] = value
