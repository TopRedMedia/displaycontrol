from displaycontrol.connections.handshake import SendAndReceiveHandshake
from displaycontrol.connections import SerialConnection
from displaycontrol.vendors import DisplayGeneric
from displaycontrol.exceptions import CommandArgumentsNotSupportedError


class BenqGeneric(DisplayGeneric):
    """
    Generic Benq Display class.
    """

    def __init__(self, connection=None, id=1):
        # If there is no connection specified, fall back to a default SerialConnection
        if connection is None:
            connection = SerialConnection()

        DisplayGeneric.__init__(self, connection, id)
        self.set_connection(connection)

    def set_connection(self, new_connection):
        new_connection.handshake = SendAndReceiveHandshake(seconds=1,
                                                           send_bytes='\r',
                                                           receive_bytes='>')
        self.connection = new_connection

    def command(self, command):
        # Add some chars.
        cmd = '*' + command + '#\r'

        # run the command
        return self.connection.runcommand(cmd)

    def command_with_response(self, data):
        response = self.command(data)

        # remove new lines
        response = ''.join(response.splitlines())

        # remove the first string if it is identical to the command
        command_length = len(data) + 2
        first_part = response[:command_length]
        if '*' + data + '#' == first_part:
            response = response[command_length:]

        # remove the * and # parts of the response if set
        if response[:1] == '*':
            response = response[1:]
        if response[-1:] == '#':
            response = response[:-1]

        # try to split the response on a =
        split = response.split('=')
        if len(split) == 2:
            return split[1]

        return response

    def get_power_state(self):
        pow = self.command_with_response('pow=?')
        if pow == 'ON':
            return self.POWER_STATE_ON
        if pow == 'OFF':
            return self.POWER_STATE_OFF
        return self.POWER_STATE_UNKNOWN

    def set_power_state(self, state):
        if state == self.POWER_STATE_ON:
            self.command('pow=on')
        elif state == self.POWER_STATE_OFF:
            self.command('pow=off')
        else:
            raise CommandArgumentsNotSupportedError()

    def get_input_channel(self):
        return self.command_with_response('sour=?')

    def get_input_channel_hr(self):
        source = self.command_with_response('sour=?')
        if source in self.input_channel_get:
            return self.input_channel_get[source]
        return source

    def set_input_channel(self, channel):
        if channel in self.input_channel_get:
            self.command_with_response('sour=' + channel)
        else:
            raise CommandArgumentsNotSupportedError()

    def get_platform_version(self):
        return self.get_platform_label()

    def get_platform_label(self):
        return self.command_with_response('modelname=?')

    def get_firmware_version(self):
        return self.get_platform_label()

    def get_firmware_build_date(self):
        return self.get_platform_label()

    def get_modell_number(self):
        return self.get_platform_label()

    def get_operating_hours(self):
        return self.get_projector_lamp_hour()

    def get_projector_lamp_hour(self):
        return self.command_with_response('ltim=?')

    def get_freeze_status(self):
        current = self.command_with_response('freeze=?')
        return self.generic_enabled_result(current)

    def set_freeze_status(self, status):
        if status == self.GENERIC_ENABLED:
            self.command('freeze=on')
        elif status == self.GENERIC_DISABLED:
            self.command('freeze=off')
        else:
            raise CommandArgumentsNotSupportedError()

    def get_blank_status(self):
        current = self.command_with_response('blank=?')
        return self.generic_enabled_result(current)

    def set_blank_status(self, status):
        if status == self.GENERIC_ENABLED:
            self.command('blank=on')
        elif status == self.GENERIC_DISABLED:
            self.command('blank=off')
        else:
            raise CommandArgumentsNotSupportedError()


class BenqLU9235(BenqGeneric):
    input_channel_get = {
        'RGB': 'COMPUTER/YPbPr',
        'RGB2': 'COMPUTER 2/YPbPr2',
        'dvid': 'DVI-D',
        'hdmi': 'HDMI 1',
        'hdmi2': 'HDMI 2 / MHL2',
        'vid': 'Composite',
        'hdbaset': 'HDbaseT',
    }
