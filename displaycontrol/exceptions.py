class VendorUnknownError(Exception):
    pass


class ConnectionUnknownError(Exception):
    pass


class CommandNotImplementedError(Exception):
    pass


class HandshakeNotSuccessfullError(Exception):
    pass


class CommandResponseMalformedError(Exception):
    pass
