import sys
import os
import pytest
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import ARP

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.realtime.flow_manager import FlowManager
from backend.realtime.packet_capture import PacketCaptureEngine


def test_tcp_packet_capture_forwarding():
    """Test 1: TCP packets are captured and forwarded to FlowManager."""
    fm = FlowManager()
    engine = PacketCaptureEngine(flow_manager=fm)
    engine.is_running = True

    pkt = IP(src="192.168.1.20", dst="8.8.8.8") / TCP(sport=54321, dport=80, flags="S")
    engine.process_packet(pkt)

    assert engine.captured_count == 1
    assert engine.ignored_count == 0
    assert fm.get_active_flow_count() == 1

    flow = fm.get_active_flows()[0]
    assert flow.source_ip == "192.168.1.20"
    assert flow.destination_ip == "8.8.8.8"
    assert flow.protocol == "TCP"


def test_udp_packet_capture_forwarding():
    """Test 2: UDP packets are captured and forwarded to FlowManager."""
    fm = FlowManager()
    engine = PacketCaptureEngine(flow_manager=fm)
    engine.is_running = True

    pkt = IP(src="10.0.0.5", dst="1.1.1.1") / UDP(sport=53535, dport=53)
    engine.process_packet(pkt)

    assert engine.captured_count == 1
    assert engine.ignored_count == 0
    assert fm.get_active_flow_count() == 1

    flow = fm.get_active_flows()[0]
    assert flow.source_ip == "10.0.0.5"
    assert flow.destination_ip == "1.1.1.1"
    assert flow.protocol == "UDP"


def test_unsupported_packets_ignored():
    """Test 3: ARP and non-IPv4/TCP/UDP packets are ignored."""
    fm = FlowManager()
    engine = PacketCaptureEngine(flow_manager=fm)
    engine.is_running = True

    arp_pkt = ARP(pdst="192.168.1.1")
    engine.process_packet(arp_pkt)

    assert engine.captured_count == 0
    assert engine.ignored_count == 1
    assert fm.get_active_flow_count() == 0


def test_no_raw_payload_stored():
    """Test 4: Privacy check - raw packet payload content is not stored in Flow."""
    fm = FlowManager()
    engine = PacketCaptureEngine(flow_manager=fm)
    engine.is_running = True

    # Packet with raw string payload
    pkt = IP(src="192.168.1.10", dst="8.8.8.8") / TCP(sport=50000, dport=80) / b"SECRET_PASSWORD_PAYLOAD"
    engine.process_packet(pkt)

    flow = fm.get_active_flows()[0]
    # Check that flow attributes do not contain raw string payload
    flow_str = str(flow.__dict__)
    assert "SECRET_PASSWORD_PAYLOAD" not in flow_str


def test_graceful_shutdown_and_flush():
    """Test 5: Stopping capture flushes all active flows and returns completed list."""
    fm = FlowManager()
    engine = PacketCaptureEngine(flow_manager=fm)
    engine.is_running = True

    pkt1 = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1000, dport=80)
    pkt2 = IP(src="10.0.0.3", dst="10.0.0.4") / UDP(sport=2000, dport=53)

    engine.process_packet(pkt1)
    engine.process_packet(pkt2)

    assert fm.get_active_flow_count() == 2

    flows = engine.stop()
    assert engine.is_running is False
    assert len(flows) == 2
    assert fm.get_active_flow_count() == 0
