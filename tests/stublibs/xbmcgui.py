from mock import Mock

Dialog = Mock()

class ListItem(object):
    def __init__(self, name, thumbnailImage=None):
        self.name = name

    def __str__(self):
        return self.name

    addContextMenuItems = Mock()
