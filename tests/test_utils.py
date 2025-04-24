# Disable some ruff checks for this file
# ruff: noqa: ANN201, S101, D103

from datetime import UTC, datetime

from t8_client.utils import (
    decode_array,
    format_timestamp,
    format_timestamps,
    get_link_timestamp,
    parse_pmode_item,
)


def test_get_link_timestamp():
    links = [
        {
            "_links": {
                "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/LP_Turbine/MAD32CY005/AM2/1554907724"
            },
        },
        {
            "_links": {
                "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/snapshots/LP_Turbine/1554892596"
            }
        },
    ]

    expected = [1554907724, 1554892596]
    for link, exp in zip(links, expected, strict=False):
        assert get_link_timestamp(link) == exp


def test_parse_pmode_item():
    link = {
        "_links": {
            "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/LP_Turbine/MAD32CY005/AM2/"
        }
    }

    expected = {"machine": "LP_Turbine", "point": "MAD32CY005", "tag": "AM2"}
    assert parse_pmode_item(link) == expected


def test_format_timestamp():
    timestamp = 1633024800  # example timestamp
    result = format_timestamp(timestamp)
    expected = datetime.fromtimestamp(timestamp, tz=UTC).isoformat()
    assert result == expected


def test_format_timestamps():
    timestamps = [1633024800, 0, 1633111200]
    result = format_timestamps(timestamps)
    expected = [
        datetime.fromtimestamp(1633024800, tz=UTC).isoformat(),
        datetime.fromtimestamp(1633111200, tz=UTC).isoformat(),
    ]
    assert result == expected


def test_decode_array():
    zint_raw = b"eJwAkAFv/nmgZc/nB9s+aGkpf9N7D2BWMeL41sENl/mA9YNrn+/NUwZ4PX1o5H5BfBphzDJ3+jnD+5dBgYqDYZ57zL4EEzyNZ5l+q3wiYj80DPygxOyYjoEjg1qdCcspA6w6mmZKfhB9KGOwNaH9Ccbhmd+BwIJXnJjJlAFCOaNl931wfSlkHzc2/3TH2po2gmKCWJsqyAAA1TeoZJ19yn0mZYw4ygDhyNebkYIKgl2av8Zs/mg2qWNAfSF+H2b2OV8CUMrYnPCCtYFmmVXF1/z4NKZi3nxyfhRnXzvzA8LL3Z1Wg2eBcpjtw0L7hTOgYXZ8v34GaMY8iQU1zeWev4McgYOXiMKt+RAylWALfAZ/82gqPh0Hq87yny6E14CYliXBGPiaMIdfmntKf9xpjD+yCCDQAqGghJeAsZXEv4X2Iy91XiR7h3/BautARQqa0RaiGYVcgM6UZ77w9KotXV2rer9/pGtGQtkLFtMro5qFH4D3kwC9a/MfLFVcHXr/f3psoUN3DXrUbqTfhUCArpI7vAnxBCwBAAD//x6/xLY="  # noqa: E501
    array_len = 200
    first_value = -24455

    result = decode_array(zint_raw, fmt="zint")
    assert len(result) == array_len
    assert result[0] == first_value
