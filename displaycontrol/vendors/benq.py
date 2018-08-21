from displaycontrol.connections.handshake import SendAndReceiveHandshake
from displaycontrol.vendors import DisplayGeneric
from displaycontrol.tools import Tools


class BenqGeneric(DisplayGeneric):
    """ Generic Benq Display class.
    """

    def __init__(self, newconnection, id=1):
        DisplayGeneric.__init__(self, newconnection, id)
        self.set_connection(newconnection)

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
        if '*'+data+'#' == first_part:
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
            self.command('blank=off')
        elif state == self.POWER_STATE_POWERSAVE:
            if self.get_power_state() == self.POWER_STATE_ON:
                self.command('blank=on')
        elif state == self.POWER_STATE_OFF:
            self.command('pow=off')

    def get_input_channel(self):
        return self.command_with_response('sour=?')

    def set_input_channel(self, channel):
        pass

    def get_auto_detect_input_channel(self):
        pass

    def set_auto_detect_input_channel(self, setting):
        pass

    def get_failover_input_setting(self):
        pass

    def set_failover_input_setting(self, setting):
        pass

    def get_lock_keys(self):
        pass

    def get_lock_ir_remote(self):
        pass

    def set_lock_keys(self, state):
        pass

    def set_lock_ir_remote(self, state):
        pass

    def get_control_software_version(self):
        pass

    def get_platform_version(self):
        pass

    def get_platform_label(self):
        return self.command_with_response('modelname=?')

    def get_firmware_version(self):
        pass

    def get_firmware_build_date(self):
        pass

    def get_serialnumber(self):
        pass

    def get_modell_number(self):
        pass

    def get_temperature(self):
        pass

    def get_operating_hours(self):
        pass

    def is_ready_for_commands(self):
        pass


class BenqLU9235(BenqGeneric):
    pass
