from displaycontrol.connections import GenericConnection
from displaycontrol.exceptions import CommandNotImplementedError
from displaycontrol.tools import Tools


class GenericDetector:
    def __init__(self):
        pass

    _command = None
    _displays = []

    def detect_displays(self):
        raise CommandNotImplementedError()


class DisplayGeneric:
    """ Generic Display Definition

    This class is used to define general available methods to all display
    control classes. This means that states for Locking, power, etc. must
    be defined here if at least one displays supports it.
    """
    GENERIC_ENABLED = 1
    GENERIC_DISABLED = 2
    GENERIC_UNKNOWN = 0

    LOCKED_UNKNOWN = -1
    LOCKED_NONE = 0
    LOCKED_ALL = 1
    LOCKED_ALL_BUT_POWER = 2
    LOCKED_ALL_BUT_VOLUME = 3
    LOCKED_PRIMARY = 4
    LOCKED_SECONDARY = 6
    LOCKED_ALL_EXCEPT_PWRVOL = 6

    dict_lock_states = {
        LOCKED_UNKNOWN: "unknown",
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
        raise CommandNotImplementedError()

    def set_display_id(self, id):
        self.display_id = int(id)

    def set_connection(self, new_connection):
        self.connection = new_connection

    def command(self, command, data):
        raise CommandNotImplementedError()

    def command_with_response(self, data):
        raise CommandNotImplementedError()

    def generic_enabled_result(self, current):
        if current == 'on':
            return self.GENERIC_ENABLED
        elif current == 'off':
            return self.GENERIC_DISABLED
        else:
            return self.GENERIC_UNKNOWN

    @staticmethod
    def is_answer_ack(data):
        raise CommandNotImplementedError()

    def get_answer_data(self, data):
        raise CommandNotImplementedError()

    def is_ready_for_commands(self):
        raise CommandNotImplementedError()

    def get_power_state(self):
        raise CommandNotImplementedError()

    def set_power_state(self, state):
        raise CommandNotImplementedError()

    def get_power_state_hr(self):
        return self.dict_power_states[self.get_power_state()]

    def get_input_channel_hr(self):
        return self.input_channel_get[self.get_input_channel()]

    def get_input_channel(self):
        raise CommandNotImplementedError()

    def set_input_channel(self, channel):
        raise CommandNotImplementedError()

    def get_auto_detect_input_channel(self):
        raise CommandNotImplementedError()

    def set_auto_detect_input_channel(self, setting):
        raise CommandNotImplementedError()

    def get_failover_input_setting(self):
        raise CommandNotImplementedError()

    def set_failover_input_setting(self, setting):
        raise CommandNotImplementedError()

    def get_lock_keys(self):
        raise CommandNotImplementedError()

    def get_lock_keys_hr(self):
        return self.dict_lock_states[self.get_lock_keys()]

    def get_lock_ir_remote(self):
        raise CommandNotImplementedError()

    def get_lock_ir_remote_hr(self):
        return self.dict_lock_states[self.get_lock_ir_remote()]

    def set_lock_keys(self, state):
        raise CommandNotImplementedError()

    def set_lock_ir_remote(self, state):
        raise CommandNotImplementedError()

    def get_control_software_version(self):
        """ Returns the software version of the serial / ethernet control software.
        """
        raise CommandNotImplementedError()

    def get_platform_version(self):
        raise CommandNotImplementedError()

    def get_platform_label(self):
        raise CommandNotImplementedError()

    def get_firmware_version(self):
        raise CommandNotImplementedError()

    def get_firmware_build_date(self):
        raise CommandNotImplementedError()

    def get_serialnumber(self):
        raise CommandNotImplementedError()

    def get_modell_number(self):
        raise CommandNotImplementedError()

    def get_temperature(self):
        """ Get's the temperature from sensors in the display. Returns a list of
        values, even if there is only one sensore builtin.
        """
        raise CommandNotImplementedError()

    def get_operating_hours(self):
        """ Gets a value in hours how many operating hours the display has. """
        raise CommandNotImplementedError()

    def get_freeze_status(self):
        raise CommandNotImplementedError()

    def set_freeze_status(self, status):
        raise CommandNotImplementedError()

    def get_blank_status(self):
        raise CommandNotImplementedError()

    def set_blank_status(self, status):
        raise CommandNotImplementedError()

    def get_audio_mute_status(self):
        raise CommandNotImplementedError()

    def set_audio_mute_status(self, status):
        raise CommandNotImplementedError()

    def get_audio_volume(self):
        raise CommandNotImplementedError()

    def set_audio_volume_higher(self):
        raise CommandNotImplementedError()

    def set_audio_volume_lower(self):
        raise CommandNotImplementedError()

    def get_picture_mode(self):
        raise CommandNotImplementedError()

    def set_picture_mode(self, mode):
        raise CommandNotImplementedError()

    def get_picture_contrast(self):
        raise CommandNotImplementedError()

    def set_picture_contrast_higher(self):
        raise CommandNotImplementedError()

    def set_picture_contrast_lower(self):
        raise CommandNotImplementedError()

    def get_picture_brightness(self):
        raise CommandNotImplementedError()

    def set_picture_brightness_higher(self):
        raise CommandNotImplementedError()

    def set_picture_brightness_lower(self):
        raise CommandNotImplementedError()

    def get_picture_color(self):
        raise CommandNotImplementedError()

    def set_picture_color_higher(self):
        raise CommandNotImplementedError()

    def set_picture_color_lower(self):
        raise CommandNotImplementedError()

    def get_picture_sharpness(self):
        raise CommandNotImplementedError()

    def set_picture_sharpness_higher(self):
        raise CommandNotImplementedError()

    def set_picture_sharpness_lower(self):
        raise CommandNotImplementedError()

    def get_picture_color_temperature(self):
        raise CommandNotImplementedError()

    def set_picture_color_temperature(self, modus):
        raise CommandNotImplementedError()

    def get_picture_aspect_ratio(self):
        raise CommandNotImplementedError()

    def set_picture_aspect_ratio(self, modus):
        raise CommandNotImplementedError()

    def get_projector_position(self):
        raise CommandNotImplementedError()

    def set_projector_position(self, position):
        raise CommandNotImplementedError()

    def get_projector_quick_cooling(self):
        raise CommandNotImplementedError()

    def set_projector_quick_cooling(self, modus):
        raise CommandNotImplementedError()

    def get_projector_direct_power(self):
        raise CommandNotImplementedError()

    def set_projector_direct_power(self, modus):
        raise CommandNotImplementedError()

    def get_projector_autopower(self):
        raise CommandNotImplementedError()

    def set_projector_autopower(self, modus):
        raise CommandNotImplementedError()

    def get_projector_lamp_hour(self):
        raise CommandNotImplementedError()

    def get_projector_lamp_modus(self):
        raise CommandNotImplementedError()

    def set_projector_lamp_modus(self, modus):
        raise CommandNotImplementedError()


