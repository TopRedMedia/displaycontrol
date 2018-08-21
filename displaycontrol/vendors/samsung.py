"""
Samsung Display Communcation file.
"""
from displaycontrol.vendors import DisplayGeneric
from displaycontrol.connections import SerialConnection, GenericConnection
from displaycontrol.tools import Tools


class SamsungGeneric(DisplayGeneric):
    connection = GenericConnection()

    input_channel_get = {
        '14': 'PC',
        '1E': 'BNC',
        '18': 'DVI',
        '0C': 'AV',
        '04': 'S-Video',
        '08': 'Component',
        '20': 'MagicNet',
        '1F': 'DVI VIDEO',
        '30': 'RF (TV)',
        '40': 'DTV',
        '21': 'HDMI',
        '22': 'HDMI_PC',
        '23': 'HDMI2',
        '24': 'HDMI2_PC',
        '25': 'DisplayPort',
    }
    input_channel_set = input_channel_get

    def __init__(self, newconnection, newid=1):
        DisplayGeneric.__init__(self, newconnection, newid)

    def command(self, command, data=None):
        """ Perform the given command with additional data """
        # If no data was given, it is an empty array
        if data is None:
            data = []

        mapping = list()

        # Always add the header
        mapping.append(0xAA)

        # Add the command
        mapping.append(command)

        # Add the Display ID
        mapping.append(self.display_id)

        # Add the Data length
        mapping.append(len(data))
        mapping = mapping + data

        # Always add the checksum
        checksum = self.calculate_checksum(mapping)
        mapping.append(checksum)

        # Convert the mapping to bytes
        cmd = Tools.list_to_bytes(mapping)

        # run the command
        return self.connection.runcommand(cmd)

    def get_answer_data(self, data):
        """ Gets the part of the data that is used as data payload """
        if self.is_answer_ack(data):
            # The data part is the part after the first six bytes without
            # the last byte. So there have to be at least 6+1+X bytes, where
            # X is the number of data bytes. If there are not more then 7 bytes
            # the data is empty.
            if len(data) <= 7:
                return list()

            # Remove the first six bytes
            del data[0]  # First one is always AA
            del data[0]  # Was second, is first after removal of first
            del data[0]  # Was third, is first after removal of first
            del data[0]  # Was fourth, is first after removal of first
            del data[0]  # Was fifth, is first after removal of first
            del data[0]  # Was sixth, is first after removal of first

            # Remove the last byte because it is the checksum
            del data[-1]

            # Return the resulting list
            return data
        else:
            return list()

    def calculate_checksum(self, mapping):
        """ Calculate the checksum as defined in the docs """
        # Init the sum with 0
        total = 0
        for index, item in enumerate(mapping):
            # Skip the first item, because it is always the header 0xAA
            if index > 0:
                total = total + int(item)
        return total

    def is_answer_ack(self, data):
        if len(data) > 7:
            return chr(int(data[4], 16)) == "A"
        else:
            return False


class SamsungV065(SamsungGeneric):
    def get_power_state(self):
        raw = self.command(0x11)
        data = self.get_answer_data(raw)
        if len(data) > 0:
            status = int(data[0])
            if status == 0:
                return self.POWER_STATE_OFF
            elif status == 1:
                return self.POWER_STATE_ON
        return self.POWER_STATE_UNKNOWN

    def get_input_channel(self):
        raw = self.command(0x14)
        data = self.get_answer_data(raw)
        if len(data) > 0:
            return data[0]

    def get_serialnumber(self):
        raw = self.command(0x8A)
        data = self.get_answer_data(raw)
        return Tools.ascii_hex_list_to_string(data)

    def get_platform_label(self):
        raw = self.command(0x8A)
        data = self.get_answer_data(raw)
        return Tools.ascii_hex_list_to_string(data)

    def set_power_state(self, state):
        if state == self.POWER_STATE_ON:
            data = self.command(0x11, [0x01])
            return self.is_answer_ack(data)
        elif state == self.POWER_STATE_OFF:
            data = self.command(0x11, [0x02])
            return self.is_answer_ack(data)
        else:
            return False

    def set_input_channel(self, channel, visible=False):
        """ Set the input channel based on the local list """
        for key in self.input_channel_set:
            if self.input_channel_set[key] == channel:
                self.command(0x14, [int(key, 16)])
                data = self.get_input_channel()
                return key == data
        return False


# noinspection PyBroadException
class SamsungSerialDetector(object):
    def __init__(self):
        self._connection = SerialConnection()
        self._command = SamsungV065(self._connection)
        self._displays = []

    def detect_displays(self):
        print "Check Samsung Displays"
        for port in Tools.get_available_comports():
            print "  -> Trying to detect on port " + str(port)
            self._command.connection.port = port
            for i in range(0, 5):
                print "    -> For Display ID " + str(i)
                self._command.set_display_id(i)
                try:
                    state = self._command.get_power_state()
                    if state != DisplayGeneric.POWER_STATE_UNKNOWN:
                        power = 'unbek.'
                        try:
                            power = self._command.get_power_state_hr()
                        except Exception:
                            pass
                        serial = ''
                        try:
                            serial = self._command.get_serialnumber()
                        except Exception:
                            pass
                        source = 'unbek.'
                        try:
                            source = self._command.get_input_channel_hr()
                        except Exception:
                            pass
                        label = 'unbekt.'
                        try:
                            label = self._command.get_platform_label()
                        except Exception:
                            pass
                        sicp = ''
                        try:
                            sicp = self._command.get_control_software_version()
                        except Exception:
                            pass

                        newdisplay = {"port": port,
                                      "id": i,
                                      "key": "samsung_generic",
                                      "label": label,
                                      "power": power,
                                      "input": source,
                                      "serial": serial,
                                      "sicp": sicp
                                      }

                        print "      -> Found new display " + str(newdisplay)

                        self._displays.append(newdisplay)

                except Exception:
                    pass

        return self._displays
