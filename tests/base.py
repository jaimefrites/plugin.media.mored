import unittest
from mock import patch

class TestCase(unittest.TestCase):
    def apply_patch(self, pathname, stub=None):
        if stub is not None:
            p = patch(pathname, stub)
            p.start()
        else:
            p = patch(pathname)
            stub = p.start()
        self.addCleanup(p.stop)
        return stub
