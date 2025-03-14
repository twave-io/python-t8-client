from datetime import UTC, datetime

import requests


def parse_wave_link(link: dict) -> datetime:
    """Parse a wave link returning the timestamp as a datetime.
    Example of a wave link:
    {
        "_links": {
            "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/LP_Turbine/MAD32CY005/AM2/1554907724"
        }
    },
    """
    self = link["_links"]["self"]
    timestamp = int(self.split("/")[-1])
    return datetime.fromtimestamp(timestamp, tz=UTC)


class T8:
    def __init__(self, host, user, password):
        self.__host = host
        self.__user = user
        self.__passw = password
        self.__base_url = f"{self.__host}/rest"

    def __request(self, url: str) -> dict:
        """Make a request to the T8 API."""
        r = requests.get(f"{self.__base_url}/{url}", auth=(self.__user, self.__passw))
        r.raise_for_status()
        return r.json()

    def __list_waves(self, mach: str, point: str, pmode: str) -> dict:
        """List available waves for a given machine, point, and processing mode."""
        return self.__request(f"waves/{mach}/{point}/{pmode}")

    def __get_wave(self, mach, point, pmode, t=0, array_fmt="zlib"):
        """Get a waveform using the T8 API.
        If no specific timestamp is provided, it returns the last available wave.
        """
        return self.__request(f"waves/{mach}/{point}/{pmode}/{t}?array_fmt={array_fmt}")

    def list_waves(self, mach: str, point: str, pmode: str) -> list[datetime]:
        """List available waves for a given machine, point, and processing mode."""
        links = self.__list_waves(mach, point, pmode)
        items = links["_items"]
        return [parse_wave_link(link) for link in items]

    def get_wave(self, mach, point, pmode, t=0, array_fmt="zlib"):
        """Get a waveform using the T8 API."""
        return self.__get_wave(mach, point, pmode, t, array_fmt)

        # print(ret)

        # factor = float(ret.get("factor", 1))
        # raw = ret["data"]
        # data = decode_array(raw, array_fmt)
        # srate = float(ret["sample_rate"])

        # wave = {
        #     "srate": srate,
        #     "data": factor * data,
        # }
        # return wave
