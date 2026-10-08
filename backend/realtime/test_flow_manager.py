import pytest
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import ARP

from backend.realtime.flow_manager import FlowManager, Flow


def test_single_tcp_packet_creates_flow():
    """TEST 1: Single TCP packet creates one flow."""
    fm = FlowManager()
    pkt = IP(src="192.168.1.10", dst="8.8.8.8") / TCP(sport=50000, dport=443, flags="S")
    res = fm.process_packet(pkt, override_time=100.0)

    assert res is None  # Flow is active
    assert fm.get_active_flow_count() == 1
    active_flows = fm.get_active_flows()
    assert len(active_flows) == 1
    flow = active_flows[0]
    assert flow.source_ip == "192.168.1.10"
    assert flow.destination_ip == "8.8.8.8"
    assert flow.source_port == 50000
    assert flow.destination_port == 443
    assert flow.protocol == "TCP"


def test_forward_tcp_packets_increment_forward_count():
    """TEST 2: Forward TCP packets increment forward count."""
    fm = FlowManager()
    pkt1 = IP(src="192.168.1.10", dst="8.8.8.8") / TCP(sport=50000, dport=443)
    pkt2 = IP(src="192.168.1.10", dst="8.8.8.8") / TCP(sport=50000, dport=443)

    fm.process_packet(pkt1, override_time=100.0)
    fm.process_packet(pkt2, override_time=101.0)

    flow = fm.get_active_flows()[0]
    assert flow.forward_packet_count == 2
    assert flow.backward_packet_count == 0
    assert flow.packet_count == 2


def test_reverse_tcp_packet_increments_backward_count():
    """TEST 3 & TEST 4: Forward + reverse packets remain one bidirectional flow."""
    fm = FlowManager()
    pkt_fwd = IP(src="192.168.1.10", dst="8.8.8.8") / TCP(sport=50000, dport=443)
    pkt_bwd = IP(src="8.8.8.8", dst="192.168.1.10") / TCP(sport=443, dport=50000)

    fm.process_packet(pkt_fwd, override_time=100.0)
    fm.process_packet(pkt_bwd, override_time=101.0)

    assert fm.get_active_flow_count() == 1
    flow = fm.get_active_flows()[0]
    assert flow.forward_packet_count == 1
    assert flow.backward_packet_count == 1
    assert flow.packet_count == 2


def test_packet_lengths_accumulated():
    """TEST 5: Packet lengths are correctly accumulated."""
    fm = FlowManager()
    pkt1 = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1234, dport=80)
    pkt2 = IP(src="10.0.0.2", dst="10.0.0.1") / TCP(sport=80, dport=1234)

    fm.process_packet(pkt1, override_time=10.0)
    fm.process_packet(pkt2, override_time=11.0)

    flow = fm.get_active_flows()[0]
    assert flow.forward_bytes == len(pkt1)
    assert flow.backward_bytes == len(pkt2)
    assert flow.total_bytes == len(pkt1) + len(pkt2)
    assert len(flow.forward_packet_lengths) == 1
    assert len(flow.backward_packet_lengths) == 1


def test_tcp_flags_counted():
    """TEST 6: TCP flags are correctly counted."""
    fm = FlowManager()
    pkt_syn = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1000, dport=80, flags="S")
    pkt_ack = IP(src="10.0.0.2", dst="10.0.0.1") / TCP(sport=80, dport=1000, flags="A")
    pkt_psh = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1000, dport=80, flags="PA")

    fm.process_packet(pkt_syn, override_time=1.0)
    fm.process_packet(pkt_ack, override_time=2.0)
    fm.process_packet(pkt_psh, override_time=3.0)

    flow = fm.get_active_flows()[0]
    assert flow.tcp_flags["syn"] == 1
    assert flow.tcp_flags["ack"] == 2
    assert flow.tcp_flags["psh"] == 1


def test_fin_closes_flow():
    """TEST 7: FIN closes the flow."""
    fm = FlowManager()
    pkt_syn = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1000, dport=80, flags="S")
    pkt_fin = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1000, dport=80, flags="FA")

    fm.process_packet(pkt_syn, override_time=1.0)
    completed = fm.process_packet(pkt_fin, override_time=2.0)

    assert completed is not None
    assert completed.fin_seen is True
    assert completed.active is False
    assert fm.get_active_flow_count() == 0


def test_rst_closes_flow():
    """TEST 8: RST closes the flow."""
    fm = FlowManager()
    pkt_syn = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1000, dport=80, flags="S")
    pkt_rst = IP(src="10.0.0.2", dst="10.0.0.1") / TCP(sport=80, dport=1000, flags="R")

    fm.process_packet(pkt_syn, override_time=1.0)
    completed = fm.process_packet(pkt_rst, override_time=2.0)

    assert completed is not None
    assert completed.rst_seen is True
    assert completed.active is False
    assert fm.get_active_flow_count() == 0


def test_idle_timeout_closes_flow():
    """TEST 9: Idle timeout closes the flow."""
    fm = FlowManager(idle_timeout=15.0)
    pkt1 = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1000, dport=80)

    fm.process_packet(pkt1, override_time=100.0)
    assert fm.get_active_flow_count() == 1

    # Expire after 16 seconds idle time
    expired = fm.expire_flows(current_time=116.0)
    assert len(expired) == 1
    assert expired[0].active is False
    assert fm.get_active_flow_count() == 0


def test_active_timeout_closes_flow():
    """TEST 10: Active timeout closes the flow."""
    fm = FlowManager(active_timeout=120.0)
    pkt1 = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1000, dport=80)

    fm.process_packet(pkt1, override_time=100.0)

    # Expire after 125 seconds total duration
    expired = fm.expire_flows(current_time=225.0)
    assert len(expired) == 1
    assert expired[0].active is False
    assert fm.get_active_flow_count() == 0


def test_udp_flows_supported():
    """TEST 11: UDP flows are supported."""
    fm = FlowManager()
    pkt_udp = IP(src="192.168.1.50", dst="1.1.1.1") / UDP(sport=5353, dport=53)

    res = fm.process_packet(pkt_udp, override_time=50.0)
    assert res is None
    assert fm.get_active_flow_count() == 1
    flow = fm.get_active_flows()[0]
    assert flow.protocol == "UDP"
    assert flow.source_port == 5353
    assert flow.destination_port == 53


def test_unsupported_packets_ignored():
    """TEST 12: ARP/unsupported packets are ignored."""
    fm = FlowManager()
    arp_pkt = ARP(pdst="192.168.1.1")

    res = fm.process_packet(arp_pkt, override_time=10.0)
    assert res is None
    assert fm.get_active_flow_count() == 0


def test_multiple_independent_flows_remain_separate():
    """TEST 13: Multiple independent flows remain separate."""
    fm = FlowManager()
    pkt1 = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1000, dport=80)
    pkt2 = IP(src="10.0.0.3", dst="10.0.0.4") / TCP(sport=2000, dport=443)

    fm.process_packet(pkt1, override_time=1.0)
    fm.process_packet(pkt2, override_time=2.0)

    assert fm.get_active_flow_count() == 2


def test_flush_all_clears_memory():
    """TEST 14: flush_all() returns all active flows and clears memory."""
    fm = FlowManager()
    pkt1 = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1000, dport=80)
    pkt2 = IP(src="10.0.0.3", dst="10.0.0.4") / UDP(sport=2000, dport=53)

    fm.process_packet(pkt1, override_time=1.0)
    fm.process_packet(pkt2, override_time=2.0)

    flushed = fm.flush_all(current_time=5.0)
    assert len(flushed) == 2
    assert fm.get_active_flow_count() == 0
    assert all(f.active is False for f in flushed)
