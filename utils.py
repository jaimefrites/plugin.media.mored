"""Utility classes."""

import re

class KeyboardView(object):
    """A view provides a keyboard dialog.  After user enters data control is
    delegated to process method.  The process method can ask the view to show
    keyboard again or finish the work.
    
    """
    keyboard_class = None

    def __call__(self):
        kbd = self.keyboard_class()  # pylint: disable=E1102

        processed = False
        keyboard_canceled = False
        while not (processed or keyboard_canceled):
            kbd.doModal()
            if kbd.isConfirmed():
                user_input = kbd.getText()
                try:
                    self.process(user_input)
                    processed = True
                except self.AskAgain:
                    pass
            else:
                keyboard_canceled = True

    def process(self, user_input):
        """Do the work or command to reask a user."""
        raise self.AskAgain

    class AskAgain(Exception):
        pass


class Match(object):
    """Regular expression match function with memory."""
    def __init__(self, str=None):
        self._str = str
        self._match = None

    def __call__(self, regexp, str=None):
        str = str or self._str
        self._match = re.match(regexp, str)
        return self._match

    def group(self, index):
        """Return the given group captured in the last successfull match."""
        return self._match.group(index)
