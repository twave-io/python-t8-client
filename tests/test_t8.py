from datetime import UTC, datetime

from t8_client.t8 import parse_wave_link


def test_parse_wave_link():
    link = {
        "_links": {
            "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/LP_Turbine/MAD32CY005/AM2/1554907724"
        }
    }

    assert parse_wave_link(link) == datetime(2019, 4, 10, 14, 48, 44, tzinfo=UTC)
