from displaycontrol.vendors import DisplayGeneric
from displaycontrol.connections import SerialConnection
from displaycontrol.tools import Tools
from displaycontrol.exceptions import CommandNotImplementedError


class PhilipsGeneric(DisplayGeneric):
    """
    Generic Philips Display class
    """

    def __init__(self, newconnection, id=1):
        DisplayGeneric.__init__(self, newconnection, id)

    def command(self, command, data):
        temp = list()

        # Add the Display ID
        temp.append(self.display_id)

        # Add the command
        temp.append(command)

        # Add the Data length
        if len(data) > 0:
            temp = temp + data

        # Generate the message size
        mapping = list()
        length = len(temp) + 2
        mapping.append(length)
        mapping = mapping + temp

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
            # The data part starts at the third byte and has a checksum

            # Remove the first two bytes
            del data[0]  # First one
            del data[0]  # Was second, is first after removal of first

            # Remove the last byte because it is the checksum
            del data[-1]

            # Return the resulting list
            return data

        else:
            return list()

    def calculate_checksum(self, mapping):
        # Init the sum with 0
        xor = 0x00
        for index, item in enumerate(mapping):
            xor = xor ^ item
        return xor

    def is_ready_for_commands(self):
        data = self.command(0x19, list())
        return self.is_answer_ack(data)


class PhilipsSICP100(PhilipsGeneric):
    """ Added to V1.0 Documentation on page 13, chapter 5.2.2"""
    input_channel_get = {
        '01': 'AV',
        '02': 'Card AV',
        '06': 'CVI 1',
        '07': 'CVI 2',
        '08': 'PC-A',
        '0A': 'HDMI 1',
        '0B': 'HDMI 2',
    }

    input_channel_set = [
        {'AV': [0x01, 0x00]},
        {'Card AV': [0x01, 0x01]},
        {'CVI 1': [0x03, 0x00]},
        {'CVI 2': [0x03, 0x01]},
        {'PC-A': [0x05, 0x00]},
        {'HDMI 1': [0x09, 0x00]},
        {'HDMI 2': [0x09, 0x01]},
    ]

    def get_control_software_version(self):
        """ Get SICP implementation version
        Added to V1.0 documentation on page 8, chapter 3.2.1 """
        raw = self.command(0xA2, [0])
        return Tools.ascii_hex_list_to_string(self.get_answer_data(raw[1:]))

    def get_platform_version(self):
        """ Get the software platform information of the platform.
        Added to V1.0 documentation on page 8, chapter 3.2.1
        Returns the same information as getPlatformLabel because it was not split
        into seperate information before SICP 1.88
        """
        return self.get_platform_label()

    def get_platform_label(self):
        """ Get the software label information of the platform.
        Added to V1.0 documentation on page 8, chapter 3.2.1. """
        raw = self.command(0xA2, [1])
        return Tools.ascii_hex_list_to_string(self.get_answer_data(raw[1:]))

    def get_power_state(self):
        """ Return the power state, according to DisplayGeneric values
        Added to V1.0 documentation on page 9, chapter 4.1.2. """
        raw = self.command(0x19, list())
        data = self.get_answer_data(raw)
        status = int(data[1])
        if status == 1:
            return self.POWER_STATE_DEEPSLEEP
        elif status == 2:
            return self.POWER_STATE_ON
        elif status == 3:
            return self.POWER_STATE_OFF
        else:
            return self.POWER_STATE_UNKNOWN

    def set_power_state(self, state):
        """ Set the power state, according to DisplayGeneric values
        Added to V1.0 documentation on page 9, chapter 4.1.3. """
        if state == self.POWER_STATE_ON:
            data = self.command(0x18, [0x02])
            return self.is_answer_ack(data)
        elif state == self.POWER_STATE_OFF:
            data = self.command(0x18, [0x03])
            return self.is_answer_ack(data)
        elif state == self.POWER_STATE_DEEPSLEEP:
            data = self.command(0x18, [0x01])
            return self.is_answer_ack(data)
        else:
            return False

    def get_lock_keys(self):
        """ Get the status of possibly locked local keyboard
        Added to V1.0 documentation on page 10, chapter 4.2 """
        raw = self.command(0x1D, list())
        data = self.get_answer_data(raw)
        if int(data[1], 16) & 1:
            return self.LOCKED_NONE
        else:
            return self.LOCKED_ALL

    def get_lock_ir_remote(self):
        """ Get the status of possibly locked IR remote
        Added to V1.0 documentation on page 10, chapter 4.2 """
        raw = self.command(0x1D, list())
        data = self.get_answer_data(raw)
        if int(data[1], 16) & 2:
            return self.LOCKED_NONE
        else:
            return self.LOCKED_ALL

    def set_lock_keys(self, state):
        """ Set the lock status of local keyboard
        Added to V1.0 documentation on page 10, chapter 4.2 """

        """ Since setting the keys always needs to set the IR
        Remote, too. We first have to check the status. """
        irstatus = self.get_lock_ir_remote()

        if irstatus == self.LOCKED_NONE:
            irflag = 0x01
        else:
            irflag = 0x00

        """ Calculate the new flag """
        if state == self.LOCKED_NONE:
            flag = irflag | 0x00
        else:
            flag = irflag | 0x02

        data = self.command(0x1D, [flag])
        return self.is_answer_ack(data)

    def set_lock_ir_remote(self, state):
        """ Set the lock status of local keyboard
        Added to V1.0 documentation on page 10, chapter 4.2 """
        raise CommandNotImplementedError()

    def get_input_channel(self):
        raw = self.command(0xAD, list())
        data = self.get_answer_data(raw)
        if len(data) >= 3:
            return data[2]

    def set_input_channel(self, channel, visible=False):
        """ Set the input channel based on the local list """
        for source in self.input_channel_set:
            for key in source:
                if channel == key:
                    label = 0x00
                    if visible:
                        label = 0x01
                    data = self.command(0xAC, [source[key][0], source[key][1], label, 0x00])
                    return self.is_answer_ack(data)
        return False

    def get_serialnumber(self):
        raw = self.command(0x15, list())
        return Tools.ascii_hex_list_to_string(self.get_answer_data(raw[1:]))

    def get_temperature(self):
        raw = self.command(0x2F, list())
        data = self.get_answer_data(raw)
        return [int(data[0], 16), int(data[1], 16)]

    def get_operating_hours(self):
        raw = self.command(0x0F, list())
        data = self.get_answer_data(raw)
        return data


class PhilipsSICP110(PhilipsSICP100):
    """ Changed in V1.1 Documentation on page 12, chapter 5.2.2"""
    input_channel_get = {
        '01': 'AV',
        '02': 'Card AV (not applicable)',
        '06': 'CVI 1',
        '07': 'CVI 2 (not applicable)',
        '08': 'PC-A',
        '0A': 'HDMI 1',
        '0B': 'HDMI 2',
    }

    input_channel_set = [
        {'AV': [0x01, 0x00]},
        {'Card AV (not applicable)': [0x01, 0x01]},
        {'CVI 1': [0x03, 0x00]},
        {'CVI 2 (not applicable)': [0x03, 0x01]},
        {'PC-A': [0x05, 0x00]},
        {'HDMI 1': [0x09, 0x00]},
        {'HDMI 2': [0x09, 0x01]},
    ]


class PhilipsSICP130(PhilipsSICP110):
    """ Changed in V1.3 Documentation on page 11, chapter 5.2.2"""
    input_channel_get = {
        '01': 'AV',
        '02': 'Card AV (not applicable)',
        '06': 'CVI 1',
        '07': 'CVI 2 (not applicable)',
        '08': 'PC-A',
        '0A': 'HDMI',
        '0B': 'DVI',
    }

    input_channel_set = [
        {'AV': [0x01, 0x00]},
        {'Card AV (not applicable)': [0x01, 0x01]},
        {'CVI 1': [0x03, 0x00]},
        {'CVI 2 (not applicable)': [0x03, 0x01]},
        {'PC-A': [0x05, 0x00]},
        {'HDMI': [0x09, 0x00]},
        {'DVI': [0x09, 0x01]},
    ]


class PhilipsSICP140(PhilipsSICP130):
    """ Changed in V1.4 Documentation on page 9, chapter 5.2.2"""
    input_channel_get = {
        '01': 'VIDEO',
        '02': 'S-VIDEO',
        '06': 'COMPONENT',
        '07': 'CVI 2 (not applicable)',
        '08': 'VGA',
        '0A': 'HDMI',
        '0B': 'DVI-D',
    }

    input_channel_set = [
        {'VIDEO': [0x01, 0x00]},
        {'S-VIDEO': [0x01, 0x01]},
        {'COMPONENT': [0x03, 0x00]},
        {'CVI 2 (not applicable)': [0x03, 0x01]},
        {'VGA': [0x05, 0x00]},
        {'HDMI': [0x09, 0x00]},
        {'DVI-D': [0x09, 0x01]},
    ]


class PhilipsSICP150(PhilipsSICP140):
    """ Changed in V1.5 Documentation on page 9, chapter 5.2.2"""
    input_channel_get = {
        '01': 'VIDEO',
        '02': 'S-VIDEO',
        '06': 'COMPONENT',
        '07': 'CVI 2 (not applicable)',
        '08': 'VGA',
        '0A': 'HDMI',
        '0B': 'DVI-D',
    }

    input_channel_set = [
        {'VIDEO': [0x01, 0x00]},
        {'S-VIDEO': [0x01, 0x01]},
        {'COMPONENT': [0x03, 0x00]},
        {'CVI 2 (not applicable)': [0x03, 0x01]},
        {'VGA': [0x05, 0x00]},
        {'HDMI': [0x09, 0x00]},
        {'DVI-D': [0x09, 0x01]},
    ]


class PhilipsSICP160(PhilipsSICP150):
    """ Changed in V1.6 Documentation on page 11, chapter 5.2.2"""
    input_channel_get = {
        '01': 'VIDEO',
        '02': 'S-VIDEO',
        '06': 'COMPONENT',
        '07': 'CVI 2 (not applicable)',
        '08': 'VGA',
        '0A': 'HDMI',
        '0B': 'DVI-D',
        '0C': 'Card DVI-D',
        '0D': 'Display Port',
        '0E': 'Card OPS',
        '0F': 'USB'
    }

    input_channel_set = [
        {'VIDEO': [0x01, 0x00]},
        {'S-VIDEO': [0x01, 0x01]},
        {'COMPONENT': [0x03, 0x00]},
        {'CVI 2 (not applicable)': [0x03, 0x01]},
        {'VGA': [0x05, 0x00]},
        {'Card DVI-D': [0x07, 0x00]},
        {'Display Port': [0x07, 0x01]},
        {'Card OPS': [0x08, 0x00]},
        {'USB': [0x08, 0x01]},
        {'HDMI': [0x09, 0x00]},
        {'DVI-D': [0x09, 0x01]},
    ]

    def get_power_state(self):
        """ Return the power state, according to DisplayGeneric values
        Return values where changed in SICP 1.6 on page 7 in chapter 4.1.2
        """
        raw = self.command(0x19, list())
        data = self.get_answer_data(raw)
        status = int(data[1])
        if status == 1:
            return self.POWER_STATE_OFF
        elif status == 2:
            return self.POWER_STATE_ON
        else:
            return self.POWER_STATE_UNKNOWN

    def set_power_state(self, state):
        """ Set the power state, according to DisplayGeneric values
        Return values where changed in SICP 1.6 on page 7 in chapter 4.1.3
        """
        if state == self.POWER_STATE_ON:
            data = self.command(0x18, [0x02])
            return self.is_answer_ack(data)
        elif state == self.POWER_STATE_OFF:
            data = self.command(0x18, [0x01])
            return self.is_answer_ack(data)
        else:
            return False


class PhilipsSICP170(PhilipsSICP160):
    """ Changed in V1.7 Documentation on page 11, chapter 5.2.2"""
    input_channel_get = {
        '01': 'VIDEO',
        '02': 'S-VIDEO',
        '06': 'COMPONENT',
        '07': 'CVI 2 (not applicable)',
        '08': 'VGA',
        '0A': 'HDMI',
        '0B': 'DVI-D',
        '0C': 'Card DVI-D (not applicable)',
        '0D': 'Display Port',
        '0E': 'Card OPS',
    }

    input_channel_set = [
        {'VIDEO': [0x01, 0x00]},
        {'S-VIDEO': [0x01, 0x01]},
        {'COMPONENT': [0x03, 0x00]},
        {'CVI 2 (not applicable)': [0x03, 0x01]},
        {'VGA': [0x05, 0x00]},
        {'Card DVI-D': [0x07, 0x00]},
        {'Display Port': [0x07, 0x01]},
        {'Card OPS': [0x08, 0x00]},
        {'HDMI': [0x09, 0x00]},
        {'DVI-D': [0x09, 0x01]},
    ]


class PhilipsSICP180(PhilipsSICP170):
    """ Changed in V1.8 Documentation, chapter 5.2.2"""
    input_channel_get = {
        '01': 'VIDEO',
        '02': 'S-VIDEO',
        '06': 'COMPONENT',
        '07': 'CVI 2 (not applicable)',
        '08': 'VGA',
        '09': 'HDMI 2',
        '0A': 'HDMI or HDMI 1',
        '0B': 'DVI-D',
        '0C': 'Card DVI-D',
        '0D': 'Display Port',
        '0E': 'Card OPS',
        '0F': 'USB'
    }

    input_channel_set = [
        {'VIDEO': [0x01, 0x00]},
        {'S-VIDEO': [0x01, 0x01]},
        {'COMPONENT': [0x03, 0x00]},
        {'CVI 2 (not applicable)': [0x03, 0x01]},
        {'VGA': [0x05, 0x00]},
        {'HDMI 2': [0x05, 0x01]},
        {'Card DVI-D': [0x07, 0x00]},
        {'Display Port': [0x07, 0x01]},
        {'Card OPS': [0x08, 0x00]},
        {'USB': [0x08, 0x01]},
        {'HDMI or HDMI 1': [0x09, 0x00]},
        {'DVI-D': [0x09, 0x01]},
    ]


class PhilipsSICP182(PhilipsSICP180):
    """ Changed in V1.82 Documentation, page 12 chapter 5.2.2"""
    input_channel_get = {
        '01': 'VIDEO',
        '02': 'S-VIDEO',
        '06': 'COMPONENT',
        '07': 'CVI 2 (not applicable)',
        '08': 'VGA',
        '09': 'HDMI 2',
        '0A': 'HDMI or HDMI 1',
        '0B': 'DVI-D',
        '0C': 'Card DVI-D',
        '0D': 'Display Port or Display Port 1',
        '0E': 'Card OPS',
        '0F': 'USB or USB 1',
        '10': 'USB 2',
        '11': 'Display Port 2'
    }

    input_channel_set = [
        {'VIDEO': [0x01, 0x00]},
        {'S-VIDEO': [0x01, 0x01]},
        {'COMPONENT': [0x03, 0x00]},
        {'CVI 2 (not applicable)': [0x03, 0x01]},
        {'VGA': [0x05, 0x00]},
        {'HDMI 2': [0x05, 0x01]},
        {'Display Port 2': [0x06, 0x00]},
        {'USB 2': [0x06, 0x01]},
        {'Card DVI-D': [0x07, 0x00]},
        {'Display Port or Display Port 1': [0x07, 0x01]},
        {'Card OPS': [0x08, 0x00]},
        {'USB or USB 1': [0x08, 0x01]},
        {'HDMI or HDMI 1': [0x09, 0x00]},
        {'DVI-D': [0x09, 0x01]},
    ]


class PhilipsSICP183(PhilipsSICP182):
    """ Changed in V1.83 Documentation, chapter 5.2.2"""
    input_channel_get = {
        '01': 'VIDEO or VIDEO 1',
        '02': 'S-VIDEO (not applicable)',
        '03': 'VIDEO 2',
        '06': 'COMPONENT',
        '07': 'CVI 2 (not applicable)',
        '08': 'VGA',
        '09': 'HDMI 2',
        '0A': 'HDMI or HDMI 1',
        '0B': 'DVI-D (not applicable)',
        '0C': 'Card DVI-D (not applicable)',
        '0D': 'Display Port or Display Port 1 (not applicable)',
        '0E': 'Card OPS (not applicable)',
        '0F': 'USB or USB 1',
        '10': 'USB 2 (not applicable)',
        '11': 'Display Port 2 (not applicable)'
    }

    input_channel_set = [
        {'VIDEO or VIDEO 1': [0x01, 0x00]},
        {'S-VIDEO (not applicable)': [0x01, 0x01]},
        {'VIDEO 2': [0x02, 0x00]},
        {'COMPONENT': [0x03, 0x00]},
        {'CVI 2 (not applicable)': [0x03, 0x01]},
        {'VGA': [0x05, 0x00]},
        {'HDMI 2': [0x05, 0x01]},
        {'Display Port 2 (not applicable)': [0x06, 0x00]},
        {'USB 2 (not applicable)': [0x06, 0x01]},
        {'Card DVI-D (not applicable)': [0x07, 0x00]},
        {'Display Port (not applicable)': [0x07, 0x01]},
        {'Card OPS (not applicable)': [0x08, 0x00]},
        {'USB or USB 1': [0x08, 0x01]},
        {'HDMI or HDMI 1': [0x09, 0x00]},
        {'DVI-D (not applicable)': [0x09, 0x01]},
    ]


class PhilipsSICP184(PhilipsSICP183):
    """ Changed in V1.84 Documentation, chapter 5.2.2"""
    input_channel_get = {
        '01': 'VIDEO',
        '02': 'S-VIDEO',
        '06': 'COMPONENT',
        '07': 'CVI 2 (not applicable)',
        '08': 'VGA',
        '09': 'HDMI 2',
        '0A': 'HDMI or HDMI 1',
        '0B': 'DVI-D',
        '0C': 'Card DVI-D',
        '0D': 'Display Port or Display Port 1',
        '0E': 'Card OPS',
        '0F': 'USB or USB 1',
        '10': 'USB 2',
        '11': 'Display Port 2'
    }

    input_channel_set = [
        {'VIDEO or VIDEO 1': [0x01, 0x00]},
        {'S-VIDEO (not applicable)': [0x01, 0x01]},
        {'COMPONENT': [0x03, 0x00]},
        {'CVI 2 (not applicable)': [0x03, 0x01]},
        {'VGA': [0x05, 0x00]},
        {'HDMI 2': [0x05, 0x01]},
        {'Display Port 2': [0x06, 0x00]},
        {'USB 2': [0x06, 0x01]},
        {'Card DVI-D': [0x07, 0x00]},
        {'Display Port or Display Port 1': [0x07, 0x01]},
        {'Card OPS': [0x08, 0x00]},
        {'USB or USB 1': [0x08, 0x01]},
        {'HDMI or HDMI 1': [0x09, 0x00]},
        {'DVI-D (not applicable)': [0x09, 0x01]},
    ]

    def get_auto_detect_input_channel(self):
        """ Get the auto detect mechanism.
          Added in V1.84 documentation on page 13, chapter 5.3 """
        raw = self.command(0xAF, list())
        data = self.get_answer_data(raw)
        if len(data) == 2:
            status = int(data[1], 16)
            if status == 0:
                return self.AUTODETECT_INPUT_OFF
            if status == 1:
                return self.AUTODETECT_INPUT_ON
        return self.AUTODETECT_INPUT_UNKNOWN

    def set_auto_detect_input_channel(self, setting):
        """ Set the auto detect mechanism. Allowed values are 0x00
        and 0x01 according to V1.84 documentation on page 13, chapter 5.3 """
        raw = self.command(0xAE, setting)
        data = self.get_answer_data(raw)
        return self.is_answer_ack(data)


class PhilipsSICP185(PhilipsSICP184):
    pass


class PhilipsSICP186(PhilipsSICP185):
    def get_answer_data(self, data):
        """ Gets the part of the data that is used as data payload """
        if self.is_answer_ack(data):
            # The data part starts at the fourth byte and has a checksum

            # Remove the first three bytes
            del data[0]  # First one
            del data[0]  # Was second, is first after removal of first
            del data[0]  # Was third, is first after removal of second

            # Remove the last byte because it is the checksum
            del data[-1]

            # Return the resulting list
            return data

        else:
            return list()

    def command(self, command, data):
        temp = list()

        # Add the Display ID As Control
        temp.append(self.display_id)

        # Add 0 as Group which means, that the Control will by done
        # by monitor ID and not by group. This is new to SICP 1.86
        temp.append(0)

        # Add the command
        temp.append(command)

        # Add the Data length
        if len(data) > 0:
            temp = temp + data

        # Generate the message size
        mapping = list()
        length = len(temp) + 2
        mapping.append(length)
        mapping = mapping + temp

        # Always add the checksum
        checksum = self.calculate_checksum(mapping)
        mapping.append(checksum)

        # Convert the mapping to bytes
        cmd = Tools.list_to_bytes(mapping)

        # run the command
        result = self.connection.runcommand(cmd)
        return result

    def get_lock_keys(self):
        """ Get the status of possibly locked local keyboard
        Changed in V1.86 documentation on page 10, chapter 4.2 """
        raw = self.command(0x1B, list())
        data = self.get_answer_data(raw)
        status = int(data[2], 16)
        if status == 0:
            return self.LOCKED_NONE
        elif status == 1:
            return self.LOCKED_ALL
        elif status == 2:
            return self.LOCKED_ALL_BUT_VOLUME
        elif status == 3:
            return self.LOCKED_ALL_BUT_POWER
        else:
            return self.LOCKED_UNKNOWN

    def get_lock_ir_remote(self):
        """ Get the status of possibly locked IR remote
        Changed in V1.86 documentation on page 10, chapter 4.2 """
        raw = self.command(0x1B, list())
        data = self.get_answer_data(raw)
        status = int(data[1], 16)
        if status == 0:
            return self.LOCKED_NONE
        elif status == 1:
            return self.LOCKED_ALL
        elif status == 2:
            return self.LOCKED_ALL_BUT_VOLUME
        elif status == 3:
            return self.LOCKED_ALL_BUT_POWER
        else:
            return self.LOCKED_UNKNOWN


class PhilipsSICP187(PhilipsSICP186):
    def get_auto_detect_input_channel(self):
        """ Get the auto detect mechanism.
          Changted in V1.87 documentation on page 19, chapter 5.3 """
        raw = self.command(0xAF, list())
        data = self.get_answer_data(raw)
        if len(data) == 2:
            status = int(data[1], 16)
            if status == 0:
                return self.AUTODETECT_INPUT_OFF
            if status == 1:
                return self.AUTODETECT_INPUT_ALL
            if status == 5:
                return self.AUTODETECT_INPUT_FAILOVER
        return self.AUTODETECT_INPUT_UNKNOWN

    pass

    def get_failover_input_setting(self):
        """ Get the input channel that are defined as failover.
        Return contains a list of input channels as hex values
        Added to V1.87 documentation on page 20, chapter 5.3.5 """
        raw = self.command(0xA6, list())
        data = self.get_answer_data(raw)
        if len(data) > 0:
            del data[0]
        return data

    def set_failover_input_setting(self, setting):
        """ Set the input channel order for automatic failover.
        Settings has to be a list. The command needs a list of exactly 14
        input chanels. If the given variable differs, it will automatically
        be trimmed to 14 entries. """

        elements = len(setting)
        needed = len(self.get_failover_input_setting())
        if elements < needed:
            for x in range(0, needed - elements):
                setting.append(00)
        elif elements > needed:
            for x in range(0, elements - needed):
                del setting[-1]
        raw = self.command(0xA5, setting)
        data = self.get_answer_data(raw)
        return self.is_answer_ack(data)


class PhilipsSICP188(PhilipsSICP187):
    """ Changed in V1.88 Documentation on page 18, chapter 5.2.2"""
    input_channel_get = {
        '01': 'VIDEO',
        '02': 'S-VIDEO',
        '03': 'COMPONENT',
        '04': 'CVI 2 (not applicable)',
        '05': 'VGA',
        '06': 'HDMI 2',
        '07': 'Display Port 2',
        '08': 'USB 2',
        '09': 'Card DVI-D',
        '0A': 'Display Port 1',
        '0B': 'Card OPS',
        '0C': 'USB 1',
        '0D': 'HDMI',
        '0E': 'DVI-D',
        '0F': 'HDMI 3',
        '10': 'BROWSER',
        '11': 'SMARCMS',
        '12': 'DMS (Digital Media Server)',
        '13': 'INTERNAL STORAGE',
        '14': 'Reserved',
        '15': 'Reserved',
    }

    input_channel_set = [
        {'VIDEO': 0x01},
        {'S-VIDEO': 0x02},
        {'COMPONENT': 0x03},
        {'CVI 2 (not applicable)': 0x04},
        {'VGA': 0x05},
        {'HDMI 2': 0x06},
        {'Display Port 2': 0x07},
        {'USB 2': 0x08},
        {'Card DVI-D': 0x09},
        {'Display Port 1': 0x0A},
        {'Card OPS': 0x0B},
        {'USB 1': 0x0C},
        {'HDMI': 0x0D},
        {'DVI-D': 0x0E},
        {'HDMI 3': 0x0F},
        {'BROWSER': 0x10},
        {'SMARTCMS': 0x11},
        {'DMS (Digital Media Server)': 0x12},
        {'INTERNAL STORAGE': 0x13},
        {'Reserved 0x14': 0x14},
        {'Reserved 0x15': 0x15},
    ]

    def get_platform_version(self):
        """ Added to V1.88 documentation on page 12, chapter 3.2.1
        """
        raw = self.command(0xA2, [2])
        return Tools.ascii_hex_list_to_string(self.get_answer_data(raw[1:]))

    def get_lock_keys(self):
        """ Get the status of possibly locked local keyboard
        Changed in V1.88 documentation on page 15, chapter 4.2.5 """
        raw = self.command(0x1B, list())
        data = self.get_answer_data(raw)
        status = int(data[1], 16)
        if status == 1:
            return self.LOCKED_NONE
        elif status == 2:
            return self.LOCKED_ALL
        elif status == 3:
            return self.LOCKED_ALL_BUT_POWER
        elif status == 4:
            return self.LOCKED_ALL_BUT_VOLUME
        elif status == 7:
            return self.LOCKED_ALL_EXCEPT_PWRVOL
        else:
            return self.LOCKED_UNKNOWN

    def set_lock_keys(self, status):
        """ Set the status of the keyboard lock
        Changed in V1.88 documentation on page 15, chapter 4.2.6 """
        if status == self.LOCKED_NONE:
            newstatus = 0x01
        elif status == self.LOCKED_ALL:
            newstatus = 0x02
        elif status == self.LOCKED_ALL_BUT_POWER:
            newstatus = 0x03
        elif status == self.LOCKED_ALL_BUT_VOLUME:
            newstatus = 0x04
        elif status == self.LOCKED_ALL_EXCEPT_PWRVOL:
            newstatus = 0x07
        else:
            return False

        data = self.command(0x1B, [newstatus])
        return self.is_answer_ack(data)

    def set_lock_ir_remote(self, status):
        """ Set the status of the IR Remote lock
        Changed in V1.88 documentation on page 15, chapter 4.2.6 """
        if status == self.LOCKED_NONE:
            newstatus = 0x01
        elif status == self.LOCKED_ALL:
            newstatus = 0x02
        elif status == self.LOCKED_ALL_BUT_POWER:
            newstatus = 0x03
        elif status == self.LOCKED_ALL_BUT_VOLUME:
            newstatus = 0x04
        elif status == self.LOCKED_PRIMARY:
            newstatus = 0x05
        elif status == self.LOCKED_SECONDARY:
            newstatus = 0x06
        elif status == self.LOCKED_ALL_EXCEPT_PWRVOL:
            newstatus = 0x07
        else:
            return False

        data = self.command(0x1C, [newstatus])
        return self.is_answer_ack(data)

    def get_lock_ir_remote(self):
        """ Get the status of possibly locked IR remote
        Changed in V1.88 documentation on page 14, chapter 4.2.2 """
        raw = self.command(0x1D, list())
        data = self.get_answer_data(raw)
        status = int(data[1], 16)
        if status == 1:
            return self.LOCKED_NONE
        elif status == 2:
            return self.LOCKED_ALL
        elif status == 3:
            return self.LOCKED_ALL_BUT_POWER
        elif status == 4:
            return self.LOCKED_ALL_BUT_VOLUME
        elif status == 5:
            return self.LOCKED_PRIMARY
        elif status == 6:
            return self.LOCKED_SECONDARY
        elif status == 7:
            return self.LOCKED_ALL_EXCEPT_PWRVOL
        else:
            return self.LOCKED_UNKNOWN

    def get_input_channel(self):
        """ Get the status of the input channel
        Changed in V1.88 documentation on page 18, chapter 5.2.2 """
        raw = self.command(0xAD, list())
        data = self.get_answer_data(raw)
        return data[1]

    def set_input_channel(self, channel, visible=False):
        """ Get the status of the input channel
        Changed in V1.88 documentation on page 17, chapter 5.2.1 """
        for source in self.input_channel_set:
            for key in source:
                if channel == key:
                    label = 0x00
                    if visible:
                        label = 0x01
                    data = self.command(0xAC, [source[key], source[key], label, 0x00])
                    return self.is_answer_ack(data)
        return False


# noinspection PyBroadException
class PhilipsSerialDetector(object):
    _command = None
    _key = None
    _connection = None
    _display = []

    def __init__(self):
        self._connection = SerialConnection()
        self._displays = []

    def detect_displays_before_sicp186(self):
        self._command = PhilipsSICP100(self._connection)
        self._key = "philips_sicp100"
        print "  -> Check Philips Displays before SICP 186"
        self.query_displays()

    def detect_displays_after_sicp186(self):
        self._command = PhilipsSICP186(self._connection)
        self._key = "philips_sicp186"
        print "Check Philips Displays after SICP 186"
        self.query_displays()

    def query_displays(self):

        for port in Tools.get_available_comports():
            print "  -> Trying to detect on port " + str(port)
            self._command.connection.setPort(port)
            for i in range(1, 5):
                print "    -> For Display ID " + str(i)
                self._command.set_display_id(i)
                try:
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

                    newdisplay = {
                        "port": port,
                        "id": i,
                        "key": self._key,
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

    def detect_displays(self):
        self.detect_displays_before_sicp186()
        self.detect_displays_after_sicp186()

        return self._displays
