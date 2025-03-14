import requests

from .utils import decode_array, parse_pmode_item, parse_wave_item


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

    def __list_wave_modes(self) -> dict:
        """List available processing modes."""
        return self.__request("waves")

    def __list_waves(self, mach: str, point: str, pmode: str) -> dict:
        """List available waves for a given machine, point, and processing mode."""
        return self.__request(f"waves/{mach}/{point}/{pmode}")

    def __get_wave(self, mach, point, pmode, t=0, array_fmt="zlib"):
        """Get a waveform using the T8 API.
        If no specific timestamp is provided, it returns the last available wave.
        """
        return self.__request(f"waves/{mach}/{point}/{pmode}/{t}?array_fmt={array_fmt}")

    def __list_spectra(self, mach: str, point: str, pmode: str) -> dict:
        """List available spectra for a given machine, point, and processing mode."""
        return self.__request(f"spectra/{mach}/{point}/{pmode}")

    def __get_spectrum(self, mach, point, pmode, t=0, array_fmt="zlib"):
        """Get a spectrum using the T8 API.
        If no specific timestamp is provided, it returns the last available spectrum.
        """
        return self.__request(
            f"spectra/{mach}/{point}/{pmode}/{t}?array_fmt={array_fmt}"
        )

    def list_proc_modes(self) -> list[dict]:
        """List available processing modes."""
        links = self.__list_wave_modes()
        items = links["_items"]
        return [parse_pmode_item(link) for link in items]

    def list_wave_modes(self) -> list[str]:
        """List available processing modes."""
        links = self.__list_wave_modes()
        items = links["_items"]
        return [item["name"] for item in items]

    def list_waves(self, mach: str, point: str, pmode: str) -> list[int]:
        """List available waves for a given machine, point, and processing mode."""
        links = self.__list_waves(mach, point, pmode)
        items = links["_items"]
        return [parse_wave_item(link) for link in items]

    def get_wave(self, mach, point, pmode, t=0, array_fmt="zint"):
        """Get a waveform using the T8 API."""
        ret = self.__get_wave(mach, point, pmode, t, array_fmt)

        data = decode_array(ret["data"], array_fmt)
        wave = {
            "srate": ret["sample_rate"],
            "data": data * ret["factor"],
            "t": ret["t"],
        }
        return wave

    def list_spectra(self, mach: str, point: str, pmode: str) -> list[int]:
        """List available spectra for a given machine, point, and processing mode."""
        links = self.__list_spectra(mach, point, pmode)
        items = links["_items"]
        return [parse_wave_item(link) for link in items]

    def get_spectrum(self, mach, point, pmode, t=0, array_fmt="zint"):
        """Get a spectrum using the T8 API."""
        ret = self.__get_spectrum(mach, point, pmode, t, array_fmt)

        data = decode_array(ret["data"], array_fmt)
        spectrum = {
            "min_freq": ret["min_freq"],
            "max_freq": ret["max_freq"],
            "data": data * ret["factor"],
            "window": ret["window"],
            "t": ret["t"],
        }
        return spectrum
