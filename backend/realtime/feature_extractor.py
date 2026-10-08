import numpy as np
from typing import Dict, List, Any
from backend.realtime.flow_manager import Flow
from backend.services.ml_service import EXPECTED_MODEL_FEATURES


def sanitize_val(val: Any) -> float:
    """Ensures value is float, non-NaN, non-Inf, and finite."""
    try:
        f = float(val)
        if not np.isfinite(f) or np.isnan(f):
            return 0.0
        return f
    except (ValueError, TypeError):
        return 0.0


def calc_stats(arr: List[float]) -> Dict[str, float]:
    """Computes max, min, mean, std, and variance for a list of numbers."""
    if not arr:
        return {"max": 0.0, "min": 0.0, "mean": 0.0, "std": 0.0, "var": 0.0}
    
    np_arr = np.array(arr, dtype=np.float64)
    if len(np_arr) == 1:
        v = float(np_arr[0])
        return {"max": v, "min": v, "mean": v, "std": 0.0, "var": 0.0}

    return {
        "max": sanitize_val(np.max(np_arr)),
        "min": sanitize_val(np.min(np_arr)),
        "mean": sanitize_val(np.mean(np_arr)),
        "std": sanitize_val(np.std(np_arr, ddof=1)),
        "var": sanitize_val(np.var(np_arr, ddof=1))
    }


def calc_iats(timestamps: List[float]) -> List[float]:
    """Computes Inter-Arrival Times (in microseconds) from seconds timestamps."""
    if len(timestamps) < 2:
        return []
    np_ts = np.array(timestamps, dtype=np.float64)
    diffs_sec = np.diff(np_ts)
    # Convert seconds to microseconds
    diffs_us = diffs_sec * 1_000_000.0
    return [max(0.0, sanitize_val(d)) for d in diffs_us]


class FeatureExtractor:
    """
    CICIDS2017 78-Feature Extractor for SecureNet AI Real-Time Pipeline.

    Converts a completed Flow object into the exact 78 numeric feature dictionary
    required by the trained XGBoost Model 5 and Isolation Forest V3.
    """

    @staticmethod
    def extract_features(flow: Flow) -> Dict[str, float]:
        """
        Extracts 78 CICIDS2017 features from a Flow instance.
        Returns a dictionary keyed by exact feature names in expected model order.
        """
        # Duration in microseconds
        duration_sec = flow.duration
        duration_us = max(0.0, duration_sec * 1_000_000.0)

        # Basic packet counts & bytes
        fwd_pkts = float(flow.forward_packet_count)
        bwd_pkts = float(flow.backward_packet_count)
        total_pkts = float(flow.packet_count)

        fwd_bytes = float(flow.forward_bytes)
        bwd_bytes = float(flow.backward_bytes)
        total_bytes = float(flow.total_bytes)

        # All packet lengths
        all_pkt_lengths = flow.forward_packet_lengths + flow.backward_packet_lengths

        # Packet length statistics
        fwd_stats = calc_stats(flow.forward_packet_lengths)
        bwd_stats = calc_stats(flow.backward_packet_lengths)
        all_stats = calc_stats(all_pkt_lengths)

        # Rates (per second)
        flow_bytes_per_sec = sanitize_val(total_bytes / duration_sec) if duration_sec > 0 else 0.0
        flow_pkts_per_sec = sanitize_val(total_pkts / duration_sec) if duration_sec > 0 else 0.0
        fwd_pkts_per_sec = sanitize_val(fwd_pkts / duration_sec) if duration_sec > 0 else 0.0
        bwd_pkts_per_sec = sanitize_val(bwd_pkts / duration_sec) if duration_sec > 0 else 0.0

        # All Timestamps combined & sorted for Flow IAT
        all_timestamps = sorted(flow.forward_timestamps + flow.backward_timestamps)

        # Inter-Arrival Times (in microseconds)
        flow_iats = calc_iats(all_timestamps)
        fwd_iats = calc_iats(flow.forward_timestamps)
        bwd_iats = calc_iats(flow.backward_timestamps)

        flow_iat_stats = calc_stats(flow_iats)
        fwd_iat_stats = calc_stats(fwd_iats)
        bwd_iat_stats = calc_stats(bwd_iats)

        fwd_iat_total = max(0.0, sanitize_val(sum(fwd_iats)))
        bwd_iat_total = max(0.0, sanitize_val(sum(bwd_iats)))

        # Header lengths (assuming average 20 bytes IP + 20 bytes TCP/UDP if unspecified)
        fwd_header_len = fwd_pkts * 20.0
        bwd_header_len = bwd_pkts * 20.0

        # Ratios & Averages
        down_up_ratio = sanitize_val(bwd_pkts / fwd_pkts) if fwd_pkts > 0 else 0.0
        avg_pkt_size = sanitize_val(total_bytes / total_pkts) if total_pkts > 0 else 0.0
        avg_fwd_seg_size = sanitize_val(fwd_bytes / fwd_pkts) if fwd_pkts > 0 else 0.0
        avg_bwd_seg_size = sanitize_val(bwd_bytes / bwd_pkts) if bwd_pkts > 0 else 0.0

        # Active & Idle calculation
        # Idle periods: gaps in flow_iats >= 1,000,000 us (1 second)
        idle_times = [iat for iat in flow_iats if iat >= 1_000_000.0]
        if idle_times:
            idle_stats = calc_stats(idle_times)
            active_times = [iat for iat in flow_iats if iat < 1_000_000.0]
            active_stats = calc_stats(active_times) if active_times else calc_stats([duration_us])
        else:
            idle_stats = {"max": 0.0, "min": 0.0, "mean": 0.0, "std": 0.0}
            active_stats = calc_stats([duration_us]) if duration_us > 0 else {"max": 0.0, "min": 0.0, "mean": 0.0, "std": 0.0}

        # Count active data packets in forward direction (packets with length > 40 bytes)
        act_data_pkt_fwd = sum(1 for l in flow.forward_packet_lengths if l > 40)

        # TCP Window / Segment defaults
        init_win_fwd = float(flow.init_win_forward)
        init_win_bwd = float(flow.init_win_backward)
        min_seg_size_fwd = 20.0

        # Raw feature map matching exact CICIDS2017 keys
        feature_map: Dict[str, float] = {
            "Destination Port": float(flow.destination_port),
            "Flow Duration": sanitize_val(duration_us),
            "Total Fwd Packets": fwd_pkts,
            "Total Backward Packets": bwd_pkts,
            "Total Length of Fwd Packets": fwd_bytes,
            "Total Length of Bwd Packets": bwd_bytes,
            "Fwd Packet Length Max": fwd_stats["max"],
            "Fwd Packet Length Min": fwd_stats["min"],
            "Fwd Packet Length Mean": fwd_stats["mean"],
            "Fwd Packet Length Std": fwd_stats["std"],
            "Bwd Packet Length Max": bwd_stats["max"],
            "Bwd Packet Length Min": bwd_stats["min"],
            "Bwd Packet Length Mean": bwd_stats["mean"],
            "Bwd Packet Length Std": bwd_stats["std"],
            "Flow Bytes/s": flow_bytes_per_sec,
            "Flow Packets/s": flow_pkts_per_sec,
            "Flow IAT Mean": flow_iat_stats["mean"],
            "Flow IAT Std": flow_iat_stats["std"],
            "Flow IAT Max": flow_iat_stats["max"],
            "Flow IAT Min": flow_iat_stats["min"],
            "Fwd IAT Total": fwd_iat_total,
            "Fwd IAT Mean": fwd_iat_stats["mean"],
            "Fwd IAT Std": fwd_iat_stats["std"],
            "Fwd IAT Max": fwd_iat_stats["max"],
            "Fwd IAT Min": fwd_iat_stats["min"],
            "Bwd IAT Total": bwd_iat_total,
            "Bwd IAT Mean": bwd_iat_stats["mean"],
            "Bwd IAT Std": bwd_iat_stats["std"],
            "Bwd IAT Max": bwd_iat_stats["max"],
            "Bwd IAT Min": bwd_iat_stats["min"],
            "Fwd PSH Flags": 0.0,
            "Bwd PSH Flags": 0.0,
            "Fwd URG Flags": 0.0,
            "Bwd URG Flags": 0.0,
            "Fwd Header Length": fwd_header_len,
            "Bwd Header Length": bwd_header_len,
            "Fwd Packets/s": fwd_pkts_per_sec,
            "Bwd Packets/s": bwd_pkts_per_sec,
            "Min Packet Length": all_stats["min"],
            "Max Packet Length": all_stats["max"],
            "Packet Length Mean": all_stats["mean"],
            "Packet Length Std": all_stats["std"],
            "Packet Length Variance": all_stats["var"],
            "FIN Flag Count": float(flow.tcp_flags.get("fin", 0)),
            "SYN Flag Count": float(flow.tcp_flags.get("syn", 0)),
            "RST Flag Count": float(flow.tcp_flags.get("rst", 0)),
            "PSH Flag Count": float(flow.tcp_flags.get("psh", 0)),
            "ACK Flag Count": float(flow.tcp_flags.get("ack", 0)),
            "URG Flag Count": float(flow.tcp_flags.get("urg", 0)),
            "CWE Flag Count": float(flow.tcp_flags.get("cwe", 0)),
            "ECE Flag Count": float(flow.tcp_flags.get("ece", 0)),
            "Down/Up Ratio": down_up_ratio,
            "Average Packet Size": avg_pkt_size,
            "Avg Fwd Segment Size": avg_fwd_seg_size,
            "Avg Bwd Segment Size": avg_bwd_seg_size,
            "Fwd Header Length.1": fwd_header_len,
            "Fwd Avg Bytes/Bulk": 0.0,
            "Fwd Avg Packets/Bulk": 0.0,
            "Fwd Avg Bulk Rate": 0.0,
            "Bwd Avg Bytes/Bulk": 0.0,
            "Bwd Avg Packets/Bulk": 0.0,
            "Bwd Avg Bulk Rate": 0.0,
            "Subflow Fwd Packets": fwd_pkts,
            "Subflow Fwd Bytes": fwd_bytes,
            "Subflow Bwd Packets": bwd_pkts,
            "Subflow Bwd Bytes": bwd_bytes,
            "Init_Win_bytes_forward": init_win_fwd,
            "Init_Win_bytes_backward": init_win_bwd,
            "act_data_pkt_fwd": float(act_data_pkt_fwd),
            "min_seg_size_forward": min_seg_size_fwd,
            "Active Mean": active_stats["mean"],
            "Active Std": active_stats["std"],
            "Active Max": active_stats["max"],
            "Active Min": active_stats["min"],
            "Idle Mean": idle_stats["mean"],
            "Idle Std": idle_stats["std"],
            "Idle Max": idle_stats["max"],
            "Idle Min": idle_stats["min"],
        }

        # Build ordered dictionary matching EXACT EXPECTED_MODEL_FEATURES
        ordered_features: Dict[str, float] = {}
        for feature_name in EXPECTED_MODEL_FEATURES:
            ordered_features[feature_name] = sanitize_val(feature_map.get(feature_name, 0.0))

        return ordered_features
