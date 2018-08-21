
class GenericHandshake:
    """
    Generic handshake class that could be used to inherit from.
    """
    def __init__(self):
        pass

    def perform_handshake(self, connection):
        pass


class WaitHandshake(GenericHandshake):
    """
    Perform a handshake by simply waiting a given amount of seconds (int).
    """
    seconds = 1

    def __init__(self, seconds=1):
        GenericHandshake.__init__(self)
        self.seconds = seconds

    def perform_handshake(self, connection):
        from time import sleep
        sleep(self.seconds)


class SendAndReceiveHandshake(GenericHandshake):
    """
    Perform a handshake by sending something and receive a given response.
    """
    seconds = 1
    send_bytes = []
    receive_bytes = []

    def __init__(self, seconds=1, send_bytes=[], receive_bytes=[]):
        GenericHandshake.__init__(self)
        self.seconds = seconds
        self.send_bytes = send_bytes
        self.receive_bytes = receive_bytes

    def perform_handshake(self, connection):
        from time import sleep

        # send the given bytes
        connection.runcommand(self.send_bytes, with_handshake=False)

        # wait
        sleep(self.seconds)

        # receive bytes
        received = connection.runcommand(self.receive_bytes, with_handshake=False)
        print received

        # compare and raise exception if not the same
        pass
