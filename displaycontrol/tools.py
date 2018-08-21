import glob
import serial
import struct
import sys


# import win32service
# import win32serviceutil


class Tools:

    def __init__(self):
        pass

    @staticmethod
    def list_to_bytes(mapping):
        bytes = []
        try:
            for item in mapping:
                bytes.append(struct.pack("B", item))
            return ''.join(bytes)
        except BaseException, err:
            raise

    @staticmethod
    def list_to_string(list):
        string = ''
        for item in list:
            string = string.join(item)
        return string

    @staticmethod
    def ascii_hex_list_to_string(list):
        return ''.join(chr(int(h, 16)) for h in list)

    @staticmethod
    def get_available_comports():
        """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except Exception:
                pass
        return result
