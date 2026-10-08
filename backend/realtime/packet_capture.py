import logging
import signal
import sys
import time
from typing import Callable, List, Optional, Any
from scapy.all import sniff, conf, get_if_list, IP, TCP, UDP
from backend.realtime.flow_manager import FlowManager, Flow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("PacketCapture")


class PacketCaptureEngine:
    """
    Scapy-based Live Packet Capture Engine for SecureNet AI.

    Captures IPv4 TCP/UDP packet headers from local network interfaces,
    streams headers to FlowManager for bidirectional aggregation,
    and manages flow expiration and graceful shutdown.
    """

    def __init__(
        self,
        flow_manager: Optional[FlowManager] = None,
        interface: Optional[str] = None,
        bpf_filter: str = "ip and (tcp or udp)",
        capture_timeout: Optional[float] = None,
        packet_limit: int = 0,
        flow_callback: Optional[Callable[[Flow], None]] = None,
    ):
        self.flow_manager = flow_manager or FlowManager()
        self.interface = interface
        self.bpf_filter = bpf_filter
        self.capture_timeout = capture_timeout
        self.packet_limit = packet_limit
        self.flow_callback = flow_callback

        self.captured_count = 0
        self.ignored_count = 0
        self.completed_flows: List[Flow] = []
        self.is_running = False

    def process_packet(self, packet: Any) -> None:
        """
        Scapy packet processing callback.
        Parses headers, forwards to FlowManager, and handles completed flows.
        """
        if not self.is_running:
            return

        # Check if packet is supported IPv4 TCP/UDP
        pkt_info = self.flow_manager.extract_packet_info(packet)
        if not pkt_info:
            self.ignored_count += 1
            return

        self.captured_count += 1

        # Process packet through FlowManager
        completed_flow = self.flow_manager.process_packet(packet)
        if completed_flow:
            self._handle_completed_flow(completed_flow, "TERMINATION")

        # Periodically expire idle flows every 50 captured packets
        if self.captured_count % 50 == 0:
            expired = self.flow_manager.expire_flows()
            for ef in expired:
                self._handle_completed_flow(ef, "IDLE_TIMEOUT")

    def _handle_completed_flow(self, flow: Flow, reason: str) -> None:
        """Helper to log and collect completed flow objects."""
        self.completed_flows.append(flow)
        logger.info(
            f"Flow completed [{reason}]: {flow.flow_id} "
            f"(Fwd: {flow.forward_packet_count}, Bwd: {flow.backward_packet_count}, Bytes: {flow.total_bytes})"
        )
        if self.flow_callback:
            try:
                self.flow_callback(flow)
            except Exception as e:
                logger.error(f"Error in flow_callback: {e}")

    def start(self) -> List[Flow]:
        """
        Starts packet capture on specified interface.
        Blocks until capture_timeout, packet_limit, or KeyboardInterrupt occurs.
        """
        self.is_running = True
        target_iface = self.interface or conf.iface

        logger.info("==========================================")
        logger.info("SECURENET AI PACKET CAPTURE STARTING")
        logger.info("==========================================")
        logger.info(f"Interface: {target_iface}")
        logger.info(f"BPF Filter: '{self.bpf_filter}'")
        logger.info(f"Timeout: {self.capture_timeout if self.capture_timeout else 'Indefinite'} s")
        logger.info(f"Packet Limit: {self.packet_limit if self.packet_limit > 0 else 'Unlimited'}")
        logger.info("==========================================")

        try:
            sniff(
                iface=self.interface,
                filter=self.bpf_filter,
                prn=self.process_packet,
                timeout=self.capture_timeout,
                count=self.packet_limit,
                store=False  # Crucial: store=False avoids storing raw packets in RAM
            )
        except KeyboardInterrupt:
            logger.info("Packet capture stopped by user signal (Ctrl+C).")
        except Exception as e:
            logger.error(f"Packet capture error: {e}")
        finally:
            return self.stop()

    def stop(self) -> List[Flow]:
        """
        Stops capture cleanly, flushes all active flows, and returns completed flows.
        """
        if not self.is_running:
            return self.completed_flows

        self.is_running = False

        # Flush any remaining active flows
        flushed = self.flow_manager.flush_all()
        for ff in flushed:
            self._handle_completed_flow(ff, "FLUSH_STOP")

        logger.info("==========================================")
        logger.info("PACKET CAPTURE SUMMARY")
        logger.info("==========================================")
        logger.info(f"Packets Processed: {self.captured_count}")
        logger.info(f"Packets Ignored:   {self.ignored_count}")
        logger.info(f"Completed Flows:   {len(self.completed_flows)}")
        logger.info(f"Active Flows Left: {self.flow_manager.get_active_flow_count()}")
        logger.info("==========================================")

        return self.completed_flows


def run_10s_manual_capture():
    """Manual 10-second real packet capture demonstration."""
    print("\n==================================================")
    print("10-SECOND REAL PACKET CAPTURE DEMONSTRATION")
    print("==================================================")
    print("Capturing live network packets for 10 seconds...")

    engine = PacketCaptureEngine(
        capture_timeout=10.0,
        bpf_filter="ip and (tcp or udp)"
    )

    flows = engine.start()
    print(f"\nManual capture finished! Total completed flows: {len(flows)}")


if __name__ == "__main__":
    run_10s_manual_capture()
