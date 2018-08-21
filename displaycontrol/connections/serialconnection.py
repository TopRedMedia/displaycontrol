import serial
import time
from displaycontrol.connections import GenericConnection


class SerialConnection(GenericConnection):
    port = 'COM1'
    timeout = 2
    sleep = 1
    baudrate = 9600
    handshake = None
    parser = None
    stopbits = 1
    parity = 'N'
    bytesize = 8

    def __init__(self):
        GenericConnection.__init__(self)

    def runcommand(self, command, with_handshake=True):
        # Perform the handshake if set
        if with_handshake:
            if self.handshake is not None:
                self.handshake.perform_handshake(self)

        # Open serial port with default settings
        out = ''
        try:
            ser = serial.Serial(port=self.port,
                                baudrate=self.baudrate,
                                timeout=self.timeout,
                                bytesize=self.bytesize,
                                parity=self.parity,
                                stopbits=self.stopbits
                                )
            ser.write(command)
            time.sleep(self.sleep)

            while ser.inWaiting() > 0:
                out += ser.read(1)
            ser.close()
        except Exception, err:
            print(err)
        else:
            ser.close()

        if self.parser is not None:
            return self.parser.parse(out)
        else:
            return out
