from base64 import b64decode
from datetime import UTC, datetime
from zlib import decompress

import numpy as np


def decode_array(raw: bytes, fmt="zint"):
    """Decode a base64-encoded binary array into a numpy array.
    The format of the array is specified by the fmt parameter.
    """

    d = decompress(b64decode(raw))

    if fmt == "zint":
        return np.frombuffer(d, dtype=np.int16).astype(np.float32)

    if fmt == "zlib":
        return np.frombuffer(d, dtype=np.float32)

    if fmt == "b64":
        return np.frombuffer(d, dtype=np.float32)

    raise ValueError(f"Unknown array format {fmt}")


def parse_timestamp(timestamp: str) -> int:
    """Parse a timestamp from an ISO 8601 string."""
    return int(datetime.fromisoformat(timestamp).timestamp())


def format_timestamp(timestamp: int) -> str:
    """Format a timestamp as an ISO 8601 string."""
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


def format_timestamps(timestamps: list[int]) -> list[str]:
    """Format a list of timestamps as ISO 8601 strings.
    If a timestamp is 0, it is ignored.
    """
    return [format_timestamp(t) for t in timestamps if t]


def parse_wave_item(item: dict) -> int:
    """Parse a json item containing a link to a wave and return its timestamp.
    Example of a wave link:
    {
        "_links": {
            "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/LP_Turbine/MAD32CY005/AM2/1554907724"
        }
    },
    """
    self = item["_links"]["self"]
    return int(self.split("/")[-1])


def parse_pmode_item(item: dict) -> dict:
    """Parse a json item containing a link to a processing mode.
    Example link:
    {
        "_links": {
            "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/LP_Turbine/MAD32CY005/AM2/"
        }
    },
    """
    self = item["_links"]["self"]
    parts = self.strip("/").split("/")
    return {"machine": parts[-3], "point": parts[-2], "pmode": parts[-1]}
