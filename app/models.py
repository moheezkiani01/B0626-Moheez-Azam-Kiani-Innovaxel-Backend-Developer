from datetime import datetime, timezone


def utc_now_iso() -> str:
    """
    Returns current UTC time as an ISO string.
    UTC keeps timestamps consistent across machines.
    """
    return datetime.now(timezone.utc).isoformat()
