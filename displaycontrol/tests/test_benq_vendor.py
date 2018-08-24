from unittest import TestCase
from displaycontrol.vendors.benq import BenQLU9235
from displaycontrol.connections.testconnection import TestConnection
from displaycontrol.exceptions import HandshakeNotSuccessfullError


class TestBenQLU9235(TestCase):
    def test_is_running(self):
        """
        Just check that the test is running.

        :return:
        """
        self.assertTrue(True)

    def test__format_of_power_on_command_is_correct(self):
        """
        Make sure that the power on command has the correct syntax.

        :return:
        """
        con = TestConnection()
        ctrl = BenQLU9235(con)
        self.assertEqual(ctrl.assemble_runnable_command('pow=on', None), '*pow=on#\r')

    def test__format_of_power_ask_command_is_correct(self):
        """
        Make sure that the format of querying for current power state is successfull.

        :return:
        """
        con = TestConnection()
        ctrl = BenQLU9235(con)
        self.assertEqual(ctrl.assemble_runnable_command('pow=?', None), '*pow=?#\r')

    def test__handshake_will_fail(self):
        """
        Calling a command will fails, since the BenQ Vendor always perform a real
        handshake by asking the hardware for a certain return value. This is not
        testable without having hardware attached.

        :return:
        """
        try:
            con = TestConnection()
            ctrl = BenQLU9235(con)
            ctrl.get_power_state()
            self.assertTrue(False)
        except HandshakeNotSuccessfullError:
            self.assertTrue(True)