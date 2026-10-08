import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from scapy.layers.inet import IP, TCP
from backend.realtime.flow_manager import FlowManager

def run_demo():
    print("==================================================")
    print("SECURENET AI FLOW MANAGER SYNTHETIC DEMONSTRATION")
    print("==================================================")
    
    fm = FlowManager()
    
    # Packet 1: A -> B
    pkt1 = IP(src="192.168.1.10", dst="8.8.8.8") / TCP(sport=50000, dport=443, flags="S")
    # Packet 2: A -> B
    pkt2 = IP(src="192.168.1.10", dst="8.8.8.8") / TCP(sport=50000, dport=443, flags="A")
    # Packet 3: B -> A
    pkt3 = IP(src="8.8.8.8", dst="192.168.1.10") / TCP(sport=443, dport=50000, flags="A")
    
    print("\nProcessing Packet 1 (A -> B)...")
    fm.process_packet(pkt1, override_time=100.0)
    
    print("Processing Packet 2 (A -> B)...")
    fm.process_packet(pkt2, override_time=101.0)
    
    print("Processing Packet 3 (B -> A)...")
    fm.process_packet(pkt3, override_time=102.0)
    
    active_flows = fm.get_active_flows()
    print("\n--- DEMONSTRATION RESULTS ---")
    print(f"Total Active Flows: {len(active_flows)}")
    
    if len(active_flows) == 1:
        flow = active_flows[0]
        print(f"Flow ID: {flow.flow_id}")
        print(f"Source: {flow.source_ip}:{flow.source_port} -> Destination: {flow.destination_ip}:{flow.destination_port}")
        print(f"Forward Packets: {flow.forward_packet_count}")
        print(f"Backward Packets: {flow.backward_packet_count}")
        print(f"Total Packets: {flow.packet_count}")
        print(f"Total Bytes: {flow.total_bytes}")
        
        assert len(active_flows) == 1
        assert flow.forward_packet_count == 2
        assert flow.backward_packet_count == 1
        assert flow.packet_count == 3
        print("\nDEMONSTRATION SUCCESS: All expected flow properties match!")

if __name__ == "__main__":
    run_demo()
