"""
This module defines scapy test
"""

__author__ = """
vladbu@mellanox.com (Vlad Buslov)
"""

from scapy.all import sendp
from lnst.Common.TestsCommon import TestGeneric


class TestScapy(TestGeneric):
    def run(self):
        packet = self.get_mopt("packet")
        interface = self.get_mopt("iface")
        interval = self.get_opt("interval", default=0.5)
        count = self.get_opt("count", default=5)
        sendp(packet, inter=interval, count=count, iface=interface)
        return self.set_pass()
