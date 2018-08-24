from displaycontrol.connections import GenericConnection


class TestConnection(GenericConnection):
    handshake = None

    def __init__(self):
        GenericConnection.__init__(self)

    def runcommand(self, command, with_handshake=True):
        # Perform the handshake if set
        if with_handshake:
            if self.handshake is not None:
                self.handshake.perform_handshake(self)

        # Simply pass so that no command will run.
        pass
