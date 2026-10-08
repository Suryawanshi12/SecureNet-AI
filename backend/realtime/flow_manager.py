import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# Default Timeouts (in seconds)
IDLE_TIMEOUT = 15.0
ACTIVE_TIMEOUT = 120.0


@dataclass
class Flow:
    """
    Bidirectional Network Flow Representation.

    Tracks accumulated packet metrics, timestamps, lengths,
    and TCP flag counts for a single 5-tuple session.
    """
    flow_id: str
    source_ip: str
    source_port: int
    destination_ip: str
    destination_port: int
    protocol: str
    start_time: float
    last_seen: float
    end_time: Optional[float] = None
    
    forward_packet_count: int = 0
    backward_packet_count: int = 0
    forward_bytes: int = 0
    backward_bytes: int = 0

    forward_packet_lengths: List[int] = field(default_factory=list)
    backward_packet_lengths: List[int] = field(default_factory=list)
    forward_timestamps: List[float] = field(default_factory=list)
    backward_timestamps: List[float] = field(default_factory=list)

    tcp_flags: Dict[str, int] = field(default_factory=lambda: {
        "fin": 0, "syn": 0, "rst": 0, "psh": 0,
        "ack": 0, "urg": 0, "cwe": 0, "ece": 0
    })

    fin_seen: bool = False
    rst_seen: bool = False
    init_win_forward: int = 0
    init_win_backward: int = 0
    active: bool = True

    @property
    def packet_count(self) -> int:
        return self.forward_packet_count + self.backward_packet_count

    @property
    def total_bytes(self) -> int:
        return self.forward_bytes + self.backward_bytes

    @property
    def duration(self) -> float:
        end = self.end_time if self.end_time is not None else self.last_seen
        return max(0.0, end - self.start_time)

    def add_packet(
        self,
        pkt_len: int,
        pkt_time: float,
        is_forward: bool,
        flags: Optional[Dict[str, bool]] = None,
        window_size: int = 0
    ) -> None:
        """Accumulates a single packet into flow statistics."""
        self.last_seen = pkt_time

        if is_forward:
            self.forward_packet_count += 1
            self.forward_bytes += pkt_len
            self.forward_packet_lengths.append(pkt_len)
            self.forward_timestamps.append(pkt_time)
            if window_size > 0 and self.init_win_forward == 0:
                self.init_win_forward = window_size
        else:
            self.backward_packet_count += 1
            self.backward_bytes += pkt_len
            self.backward_packet_lengths.append(pkt_len)
            self.backward_timestamps.append(pkt_time)
            if window_size > 0 and self.init_win_backward == 0:
                self.init_win_backward = window_size

        if flags:
            for flag_name, flag_val in flags.items():
                if flag_val and flag_name in self.tcp_flags:
                    self.tcp_flags[flag_name] += 1

            if flags.get("fin"):
                self.fin_seen = True
            if flags.get("rst"):
                self.rst_seen = True


class FlowManager:
    """
    Bidirectional Flow Aggregation Manager.

    Maintains a hash table of active 5-tuple flows, handles forward/backward
    direction tracking, enforces idle and active timeouts, and manages TCP lifecycle.
    """

    def __init__(
        self,
        idle_timeout: float = IDLE_TIMEOUT,
        active_timeout: float = ACTIVE_TIMEOUT
    ):
        self.idle_timeout = idle_timeout
        self.active_timeout = active_timeout
        self.active_flows: Dict[Tuple, Flow] = {}

    @staticmethod
    def get_canonical_key(
        src_ip: str,
        src_port: int,
        dst_ip: str,
        dst_port: int,
        protocol: str
    ) -> Tuple:
        """
        Generates a canonical bidirectional flow key.
        Ensures both A -> B and B -> A produce identical hashtable keys.
        """
        endpoint1 = (src_ip, src_port)
        endpoint2 = (dst_ip, dst_port)
        if endpoint1 < endpoint2:
            return (endpoint1, endpoint2, protocol)
        else:
            return (endpoint2, endpoint1, protocol)

    def extract_packet_info(self, packet: Any) -> Optional[Dict[str, Any]]:
        """
        Safely extracts required fields from Scapy packets or mock dict packets.
        Returns None for unsupported/non-IP/non-TCP/UDP packets.
        """
        try:
            # 1. Handle Mock Dict Packets (Unit Tests)
            if isinstance(packet, dict):
                required = ["src_ip", "dst_ip", "src_port", "dst_port", "protocol"]
                if not all(k in packet for k in required):
                    return None
                return {
                    "timestamp": float(packet.get("time", time.time())),
                    "src_ip": str(packet["src_ip"]),
                    "dst_ip": str(packet["dst_ip"]),
                    "src_port": int(packet["src_port"]),
                    "dst_port": int(packet["dst_port"]),
                    "protocol": str(packet["protocol"]).upper(),
                    "packet_len": int(packet.get("length", 60)),
                    "flags": packet.get("flags", {}),
                    "window": int(packet.get("window", 0)),
                }

            # 2. Handle Scapy Packets
            # Check for IP layer
            has_ip = hasattr(packet, "haslayer") and packet.haslayer("IP")
            if not has_ip:
                return None

            ip_layer = packet["IP"]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            pkt_time = float(packet.time) if hasattr(packet, "time") else time.time()
            pkt_len = len(packet)

            # Check for TCP / UDP layers
            if packet.haslayer("TCP"):
                protocol = "TCP"
                tcp_layer = packet["TCP"]
                src_port = tcp_layer.sport
                dst_port = tcp_layer.dport
                window = int(getattr(tcp_layer, "window", 0))

                # Parse Scapy TCP flags
                raw_flags = str(tcp_layer.flags)
                flags = {
                    "fin": "F" in raw_flags,
                    "syn": "S" in raw_flags,
                    "rst": "R" in raw_flags,
                    "psh": "P" in raw_flags,
                    "ack": "A" in raw_flags,
                    "urg": "U" in raw_flags,
                    "cwe": "C" in raw_flags,
                    "ece": "E" in raw_flags,
                }
            elif packet.haslayer("UDP"):
                protocol = "UDP"
                udp_layer = packet["UDP"]
                src_port = udp_layer.sport
                dst_port = udp_layer.dport
                flags = {}
                window = 0
            else:
                # Non-TCP/UDP IP packet (e.g., ICMP, IGMP) - ignore
                return None

            return {
                "timestamp": pkt_time,
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "protocol": protocol,
                "packet_len": pkt_len,
                "flags": flags,
                "window": window,
            }
        except Exception:
            return None

    def process_packet(
        self,
        packet: Any,
        override_time: Optional[float] = None
    ) -> Optional[Flow]:
        """
        Processes an incoming packet.
        Returns the completed Flow if FIN/RST or timeout occurs, else returns None.
        """
        pkt_info = self.extract_packet_info(packet)
        if not pkt_info:
            return None

        pkt_time = override_time if override_time is not None else pkt_info["timestamp"]
        key = self.get_canonical_key(
            pkt_info["src_ip"],
            pkt_info["src_port"],
            pkt_info["dst_ip"],
            pkt_info["dst_port"],
            pkt_info["protocol"]
        )

        flow = self.active_flows.get(key)
        completed_flow: Optional[Flow] = None

        if flow is None:
            # 1. Create New Flow (Forward direction set by initial packet)
            flow_id = f"{pkt_info['src_ip']}:{pkt_info['src_port']}-{pkt_info['dst_ip']}:{pkt_info['dst_port']}-{pkt_info['protocol']}"
            flow = Flow(
                flow_id=flow_id,
                source_ip=pkt_info["src_ip"],
                source_port=pkt_info["src_port"],
                destination_ip=pkt_info["dst_ip"],
                destination_port=pkt_info["dst_port"],
                protocol=pkt_info["protocol"],
                start_time=pkt_time,
                last_seen=pkt_time
            )
            self.active_flows[key] = flow
            is_forward = True
        else:
            # 2. Match Direction against initial flow sender
            is_forward = (
                pkt_info["src_ip"] == flow.source_ip and
                pkt_info["src_port"] == flow.source_port
            )

        # Check timeouts on existing flow before adding new packet
        idle_expired = (pkt_time - flow.last_seen) >= self.idle_timeout
        active_expired = (pkt_time - flow.start_time) >= self.active_timeout

        if (idle_expired or active_expired) and flow.packet_count > 0:
            # Current flow expired before this packet; close it
            completed_flow = self._close_flow(key, flow, pkt_time)
            
            # Start new flow for this arriving packet
            flow_id = f"{pkt_info['src_ip']}:{pkt_info['src_port']}-{pkt_info['dst_ip']}:{pkt_info['dst_port']}-{pkt_info['protocol']}"
            flow = Flow(
                flow_id=flow_id,
                source_ip=pkt_info["src_ip"],
                source_port=pkt_info["src_port"],
                destination_ip=pkt_info["dst_ip"],
                destination_port=pkt_info["dst_port"],
                protocol=pkt_info["protocol"],
                start_time=pkt_time,
                last_seen=pkt_time
            )
            self.active_flows[key] = flow
            is_forward = True

        # Accumulate packet statistics
        flow.add_packet(
            pkt_len=pkt_info["packet_len"],
            pkt_time=pkt_time,
            is_forward=is_forward,
            flags=pkt_info["flags"],
            window_size=pkt_info["window"]
        )

        # Immediate TCP Termination Check (FIN or RST)
        if flow.fin_seen or flow.rst_seen:
            completed_flow = self._close_flow(key, flow, pkt_time)

        return completed_flow

    def _close_flow(self, key: Tuple, flow: Flow, end_time: float) -> Flow:
        """Internal helper to mark flow inactive and remove from active tracking."""
        flow.active = False
        flow.end_time = end_time
        if key in self.active_flows:
            del self.active_flows[key]
        return flow

    def expire_flows(self, current_time: Optional[float] = None) -> List[Flow]:
        """
        Sweeps active flows and expires any that exceed IDLE_TIMEOUT or ACTIVE_TIMEOUT.
        Returns a list of completed Flow objects.
        """
        now = current_time if current_time is not None else time.time()
        expired: List[Flow] = []
        keys_to_remove: List[Tuple] = []

        for key, flow in self.active_flows.items():
            if (now - flow.last_seen >= self.idle_timeout) or (now - flow.start_time >= self.active_timeout):
                flow.active = False
                flow.end_time = flow.last_seen
                expired.append(flow)
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.active_flows[key]

        return expired

    def get_active_flow_count(self) -> int:
        """Returns the number of currently active in-memory flows."""
        return len(self.active_flows)

    def get_active_flows(self) -> List[Flow]:
        """Returns a list of all active Flow objects."""
        return list(self.active_flows.values())

    def flush_all(self, current_time: Optional[float] = None) -> List[Flow]:
        """
        Flushes all active flows (e.g., on shutdown/reset).
        Marks them completed and clears memory.
        """
        now = current_time if current_time is not None else time.time()
        flushed: List[Flow] = []
        for flow in self.active_flows.values():
            flow.active = False
            flow.end_time = flow.last_seen if flow.last_seen else now
            flushed.append(flow)
        self.active_flows.clear()
        return flushed
