from abc import ABCMeta

from displaycontrol.vendors import DisplayGeneric
from displaycontrol.connections import GenericConnection
from displaycontrol.exceptions import NotImplementedError
from displaycontrol.tools import Tools


class BenqGeneric(DisplayGeneric):
    """ Generic Benq Display class.
    """

    def __init__(self, newconnection, id=1):
        DisplayGeneric.__init__(self, newconnection, id)
        self.set_connection(newconnection)

    def command(self, command, data):
        temp = list()

        # Add a *
        temp.append('*')

        # Add the command
        temp.append(command)

        # Add a #
        temp.append('#')

        # Convert the mapping to bytes
        cmd = Tools.list_to_string(temp)

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

    def get_power_state(self):
        raise NotImplementedError()

    def set_power_state(self, state):
        pass

    def get_input_channel(self):
        pass

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
        pass

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
        data = self.command(0x19, list())
        return self.is_answer_ack(data)


class BenqLU9235(BenqGeneric):
    pass