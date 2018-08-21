import serial, time
from displaycontrol.connections import GenericConnection


class SerialConnection(GenericConnection):
    port = 0

    def setPort(self, newport):
        self.port = newport

    def runcommand(self, command):
        # Open first serial port with default settings
        out = ''
        try:
            ser = serial.Serial(self.port)
            ser.close()
            ser.open()
            ser.write(command)
            time.sleep(0.5)  # give the display time to respond
            while ser.inWaiting() > 0:
                out += ser.read(1)
            ser.close()
        except Exception, err:
            print(err)
        else:
            ser.close()

        # unfuddle the output
        data = ''.join(["%02X " % ord(x) for x in out]).strip()
        data = data.split(' ')

        return data
