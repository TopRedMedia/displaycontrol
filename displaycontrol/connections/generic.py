from displaycontrol.exceptions import *


class GenericConnection:

    def __init__(self):
        pass

    def runcommand(self, command, with_handshake=True):
        raise CommandNotImplementedError()
