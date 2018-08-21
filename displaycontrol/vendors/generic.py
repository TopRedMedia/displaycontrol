from displaycontrol.connections import GenericConnection
from displaycontrol.exceptions import NotImplementedError
from displaycontrol.tools import Tools


class GenericDetector:
    def __init__(self):
        pass

    _command = None
    _displays = []

    def detect_displays(self):
        raise NotImplementedError()


class DisplayGeneric:
    """ Generic Display Definition

    This class is used to define general available methods to all display
    control classes. This means that states for Locking, power, etc. must
    be defined here if at least one displays supports it.
    """
    GENERIC_ENABLED = 1
    GENERIC_DISABLED = 2

    LOCKED_UNKOWN = -1
    LOCKED_NONE = 0
    LOCKED_ALL = 1
    LOCKED_ALL_BUT_POWER = 2
    LOCKED_ALL_BUT_VOLUME = 3
    LOCKED_PRIMARY = 4
    LOCKED_SECONDARY = 6
    LOCKED_ALL_EXCEPT_PWRVOL = 6

    dict_lock_states = {
        LOCKED_UNKOWN: "unknown",
        LOCKED_NONE: "No Lock",
        LOCKED_ALL: "All",
        LOCKED_ALL_BUT_POWER: "All but Power",
        LOCKED_ALL_BUT_VOLUME: "All but Volume",
        LOCKED_PRIMARY: "Primary (Master)",
        LOCKED_SECONDARY: "Secondary (Daisy chain PD)",
        LOCKED_ALL_EXCEPT_PWRVOL: "All except Power & Volume",
    }

    POWER_STATE_DEEPSLEEP = -1
    POWER_STATE_OFF = 0
    POWER_STATE_ON = 1
    POWER_STATE_POWERSAVE = 2
    POWER_STATE_UNKNOWN = 3

    dict_power_states = {
        POWER_STATE_DEEPSLEEP: "Deep Sleep / Standby",
        POWER_STATE_OFF: "Off",
        POWER_STATE_ON: "On",
        POWER_STATE_POWERSAVE: "Power Save",
        POWER_STATE_UNKNOWN: "Unknown"
    }

    AUTODETECT_INPUT_UNKNOWN = -1
    AUTODETECT_INPUT_OFF = 0
    AUTODETECT_INPUT_ON = 1
    AUTODETECT_INPUT_ALL = 2
    AUTODETECT_INPUT_FAILOVER = 3

    dict_autodetect_input = {
        AUTODETECT_INPUT_OFF: "Off",
        AUTODETECT_INPUT_ON: "On",
        AUTODETECT_INPUT_ALL: "All",
        AUTODETECT_INPUT_FAILOVER: "Failover"
    }

    """ Has to be overridden by each class because this really
    differs a lot between implementations and is only needed to
    create the HR method """
    input_channel_get = {}
    input_channel_set = []

    connection = GenericConnection()
    display_id = 1

    def __init__(self, newconnection, id=1):
        self.set_connection(newconnection)
        self.set_display_id(id)

    def detect_displays(self):
        ports = Tools.get_available_comports()
        available = []
        for port in ports:
            for id in range(5):
                if self.is_ready_for_commands():
                    available.append({"port": port, "class": self.__name__, "id": id})
        return available

    def set_display_id(self, id):
        self.display_id = int(id)

    def set_connection(self, new_connection):
        self.connection = new_connection

    @staticmethod
    def is_answer_ack(data):
        if len(data) > 2:
            return True
        else:
            return False

    def get_answer_data(self, data):
        raise NotImplementedError()

    def is_ready_for_commands(self):
        raise NotImplementedError()

    def get_power_state(self):
        raise NotImplementedError()

    def set_power_state(self, state):
        raise NotImplementedError()

    def get_power_state_hr(self):
        return self.dict_power_states[self.get_power_state()]

    def get_input_channel_hr(self):
        return self.input_channel_get[self.get_input_channel()]

    def get_input_channel(self):
        raise NotImplementedError()

    def set_input_channel(self, channel):
        raise NotImplementedError()

    def get_auto_detect_input_channel(self):
        raise NotImplementedError()

    def set_auto_detect_input_channel(self, setting):
        raise NotImplementedError()

    def get_failover_input_setting(self):
        raise NotImplementedError()

    def set_failover_input_setting(self, setting):
        raise NotImplementedError()

    def get_lock_keys(self):
        raise NotImplementedError()

    def get_lock_keys_hr(self):
        return self.dict_lock_states[self.get_lock_keys()]

    def get_lock_ir_remote(self):
        raise NotImplementedError()

    def get_lock_ir_remote_hr(self):
        return self.dict_lock_states[self.get_lock_ir_remote()]

    def set_lock_keys(self, state):
        raise NotImplementedError()

    def set_lock_ir_remote(self, state):
        raise NotImplementedError()

    def get_control_software_version(self):
        """ Returns the software version of the serial / ethernet control software.
        """
        raise NotImplementedError()

    def get_platform_version(self):
        raise NotImplementedError()

    def get_platform_label(self):
        raise NotImplementedError()

    def get_firmware_version(self):
        raise NotImplementedError()

    def get_firmware_build_date(self):
        raise NotImplementedError()

    def get_serialnumber(self):
        raise NotImplementedError()

    def get_modell_number(self):
        raise NotImplementedError()

    def get_temperature(self):
        """ Get's the temperature from sensors in the display. Returns a list of
        values, even if there is only one sensore builtin.
        """
        raise NotImplementedError()

    def get_operating_hours(self):
        """ Gets a value in hours how many operating hours the display has. """
        raise NotImplementedError()
