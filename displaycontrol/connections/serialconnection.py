import serial, time
from displaycontrol.connections import GenericConnection


class SerialConnection(GenericConnection):
    port = 0
    timeout = None
    baudrate = 9600

    def set_port(self, value):
        self.port = value

    def set_timeout(self, value):
        self.timeout = value

    def set_baudrate(self, value):
        self.baudrate = value

    def runcommand(self, command):
        # Open first serial port with default settings
        out = ''
        try:
            ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            ser.close()
            ser.open()
            ser.write(command)
            while ser.inWaiting() > 0:
                out += ser.read(1)
            ser.close()
        except Exception, err:
            print(err)
        else:
            ser.close()

        # unfuddle the output
        print out
        data = ''.join(["%02X " % ord(x) for x in out]).strip()
        data = data.split(' ')

        return data
