from base64 import b64decode
from struct import unpack
from zlib import decompress

import numpy as np


def decode_array(raw: bytes, fmt="zlib"):
    """Decode a base64-encoded binary array into a numpy array.
    The format of the array is specified by the fmt parameter.
    """
    if fmt == "zlib":
        d = decompress(b64decode(raw))
        return np.array(
            [unpack("f", d[i * 4 : (i + 1) * 4])[0] for i in range(int(len(d) / 4))],
            dtype="f",
        )
    elif fmt == "zint":
        d = decompress(b64decode(raw))
        return np.array(
            [unpack("h", d[i * 2 : (i + 1) * 2])[0] for i in range(int(len(d) / 2))],
            dtype="f",
        )
    elif fmt == "b64":
        return np.frombuffer(b64decode(raw), dtype="f")

    raise ValueError(f"Unknown array format {fmt}")
