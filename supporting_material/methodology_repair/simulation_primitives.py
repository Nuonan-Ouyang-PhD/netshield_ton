"""Public, dependency-free service primitives for corrected simulations.

These functions describe an application byte-service model.  They neither
measure Wi-Fi performance nor include unobserved detector/core computation.
The historical V1.3 allocator is retained separately under ``legacy/``.
"""

from __future__ import annotations

import math
from collections.abc import Mapping


def _nonnegative_int(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def waterfill(
    demands: Mapping[str, int], cap: int, *, tie_offset: int = 0,
) -> dict[str, int]:
    """Integer max-min allocation, consuming min(cap, total demand) bytes.

    Equal-share residual bytes go to active devices in sorted order rotated
    by ``tie_offset``.  The caller can rotate this offset between service
    intervals; the default fixes it at zero for deterministic standalone use.
    Empty or exhausted queues never receive service.
    """
    remaining = _nonnegative_int(cap, "cap")
    if isinstance(tie_offset, bool) or not isinstance(tie_offset, int):
        raise ValueError("tie_offset must be an integer")
    devices = sorted(demands)
    for device in devices:
        _nonnegative_int(demands[device], f"demand[{device}]")
    grants = dict.fromkeys(devices, 0)
    if devices:
        offset = tie_offset % len(devices)
        devices = devices[offset:] + devices[:offset]
    active = [device for device in devices if demands[device] > 0]
    while remaining and active:
        share = remaining // len(active)
        if not share:
            # Every active queue can accept at least one byte.  Here
            # remaining < len(active), so each residual byte is assigned once.
            for device in active[:remaining]:
                grants[device] += 1
            remaining = 0
            break
        for device in active:
            give = min(demands[device] - grants[device], share)
            grants[device] += give
            remaining -= give
        active = [device for device in active if grants[device] < demands[device]]
    return grants


def admission_budget(capacity_bytes: int, existing_queues: Mapping[str, int]) -> int:
    """Bytes available for new arrivals after reserving existing backlog.

    A zero budget with backlog > capacity does *not* certify that old work
    can finish in the current round.  Use ``same_round_upload_feasible`` to
    distinguish that case.  This is a byte-budget condition, not an end-to-end
    deadline guarantee.
    """
    capacity = _nonnegative_int(capacity_bytes, "capacity_bytes")
    backlog = sum(_nonnegative_int(q, f"queue[{key}]") for key, q in existing_queues.items())
    return max(0, capacity - backlog)


def same_round_upload_feasible(
    existing_queues: Mapping[str, int], new_payloads: Mapping[str, int], capacity_bytes: int,
) -> bool:
    """Whether all queued/new bytes fit one ideal work-conserving round.

    Assumptions: all listed work is available at the round start; no later
    arrivals; the server supplies capacity_bytes during that round.  Compute,
    network jitter and result return need separate budgets.
    """
    capacity = _nonnegative_int(capacity_bytes, "capacity_bytes")
    backlog = sum(_nonnegative_int(q, f"queue[{key}]") for key, q in existing_queues.items())
    arrivals = sum(_nonnegative_int(b, f"payload[{key}]") for key, b in new_payloads.items())
    return backlog + arrivals <= capacity


def isolated_latency_ms(
    payload_bytes: int, capacity_bytes_per_second: int, *, compute_ms: float = 0.0,
    core_ms: float = 0.0, fixed_network_ms: float = 0.0,
) -> float:
    """Optimistic no-competition latency estimate, never shared-link safety.

    The supplied latency terms are model inputs, not measured values.  Core
    queuing, competing uploads and returned-result service are not modeled.
    """
    payload = _nonnegative_int(payload_bytes, "payload_bytes")
    capacity = _nonnegative_int(capacity_bytes_per_second, "capacity_bytes_per_second")
    if capacity == 0:
        raise ValueError("capacity_bytes_per_second must be positive")
    terms = (compute_ms, core_ms, fixed_network_ms)
    if any(not math.isfinite(term) or term < 0 for term in terms):
        raise ValueError("latency components must be finite and nonnegative")
    return sum(terms) + 1000.0 * payload / capacity


def upload_on_time(
    origin_tick: int, completion_tick: int | None, deadline_ticks: int = 1000,
) -> bool:
    """Payload upload completes in [origin, origin + deadline], inclusive.

    ``None`` is unfinished and remains a miss.  The caller declares tick
    resolution; upload completion is not core result arrival.
    """
    origin = _nonnegative_int(origin_tick, "origin_tick")
    deadline = _nonnegative_int(deadline_ticks, "deadline_ticks")
    if completion_tick is None:
        return False
    completion = _nonnegative_int(completion_tick, "completion_tick")
    return 0 <= completion - origin <= deadline
