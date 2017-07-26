from scapy.all import Ether, IP, SCTP
from lnst.Controller.Task import ctl
from Testlib import Testlib

# ------
# SETUP
# ------

tl = Testlib(ctl)

h1 = ctl.get_host("host1")
g1 = ctl.get_host("guest1")
g2 = ctl.get_host("guest2")

# ------
# TESTS
# ------

h1_ovs_br = h1.get_interface("ovs1")
g1_guestnic = g1.get_interface("if1")
g1_mac = g1_guestnic.get_hwaddr()
g1_ip = g1_guestnic.get_ip(0)
g2_guestnic = g2.get_interface("if1")
g2_mac = g2_guestnic.get_hwaddr()
g2_ip = g2_guestnic.get_ip(0)
src_port = 1111
dst_port = 1112


def send_sctp(options={}):
    packet = (Ether(src=str(g1_mac), dst=str(g2_mac))
              / IP(src=str(g1_ip), dst=str(g2_ip))
              / SCTP(dport=dst_port, sport=src_port))
    options = dict(options)
    options.update({
        "packet": packet,
        "iface": g1_guestnic.get_devname(),
    })
    scapy_mod = ctl.get_module("TestScapy", options=options)
    g1.run(scapy_mod)


def verify_tc_rules(proto):
    m = tl.find_tc_rule(h1, 'tap1', g1_mac, g2_mac, proto, 'gact action drop')
    if m:
        tl.custom(h1, "TC rule %s vm1->vm2" % proto, opts=m)
    else:
        tl.custom(h1, "TC rule %s vm1->vm2" % proto,
                  'ERROR: cannot find tc rule')

    m = tl.find_tc_rule(h1, 'tap2', g2_mac, g1_mac, proto)
    if m:
        tl.custom(h1, "TC rule %s vm2->vm1" % proto,
                  'ERROR: tc rule should not exist')
    else:
        tl.custom(h1, "TC rule %s vm2->vm1" % proto, opts=m)


cmd_str = (
    "ovs-ofctl add-flow %s dl_src=%s,dl_dst=%s,sctp,tp_src=%u,action=drop"
    % (h1_ovs_br.get_devname(), g1_mac, g2_mac, src_port))
h1.run(cmd_str)
send_sctp()
verify_tc_rules('ip')
