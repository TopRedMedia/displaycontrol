import json, struct
import os
# import win32service
# import win32serviceutil
import serial


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
        available = []
        ports = ['COM%s' % (i + 1) for i in range(10)]
        for port in ports:
            try:
                ser = serial.Serial(port)
                ser.close()
                available.append(port)
            except Exception, err:
                ser.close()
                pass
        return available
