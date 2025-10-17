import numpy as np
import requests

from .models import (
    MachineTrend,
    ParamTrend,
    PointTrend,
    ProcModeTrend,
    Spectrum,
    Status,
    SystemInfo,
    Wave,
)
from .utils import decode_array, parse_link, parse_pmode_item


class T8:
    def __init__(self, host: str, user: str, password: str) -> None:
        self.__host = host
        self.__user = user
        self.__passw = password
        self.__base_url = f"{self.__host}/rest"

    def __build_url_with_timestamp_params(
        self, base_url: str, from_ts: int | None = None, to_ts: int | None = None
    ) -> str:
        """Build URL with optional timestamp parameters."""
        params = []
        if from_ts is not None:
            params.append(f"from={from_ts}")
        if to_ts is not None:
            params.append(f"to={to_ts}")
        if params:
            return base_url + "?" + "&".join(params)
        return base_url

    @property
    def host(self) -> str:
        """Return the host URL."""
        return self.__host

    @property
    def user(self) -> str:
        """Return the username."""
        return self.__user

    def __request(self, url: str) -> dict:
        """Make a request to the T8 API."""
        r = requests.get(
            f"{self.__base_url}/{url}",
            auth=(self.__user, self.__passw),
            allow_redirects=True,
            timeout=5,
        )
        r.raise_for_status()
        return r.json()

    def __list_params(self) -> dict:
        """List available parameters."""
        return self.__request("trends/param")

    def __list_wave_modes(self) -> dict:
        """List available processing modes."""
        return self.__request("waves")

    def __list_waves(
        self,
        mach: str,
        point: str,
        pmode: str,
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> dict:
        """List available waves for a given machine, point, and processing mode."""
        base_url = f"waves/{mach}/{point}/{pmode}"
        url = self.__build_url_with_timestamp_params(base_url, from_ts, to_ts)
        return self.__request(url)

    def __list_configs(self, from_ts: int | None = None, to_ts: int | None = None) -> dict:
        """List available configurations."""
        base_url = "confs"
        url = self.__build_url_with_timestamp_params(base_url, from_ts, to_ts)
        return self.__request(url)

    def __get_config(self, conf: str) -> dict:
        """Get a specific configuration given its ID."""
        return self.__request(f"confs/{conf}")

    def __list_snapshots(
        self, mach: str, from_ts: int | None = None, to_ts: int | None = None
    ) -> dict:
        """List available snapshots for a given machine."""
        base_url = f"snapshots/{mach}"
        url = self.__build_url_with_timestamp_params(base_url, from_ts, to_ts)
        return self.__request(url)

    def __get_snapshot(self, mach: str, t: int = 0) -> dict:
        """Get a snapshot using the T8 API.
        If no specific timestamp is provided, it returns the last available snapshot.
        """
        return self.__request(f"snapshots/{mach}/{t}")

    def __get_wave(
        self, mach: str, point: str, pmode: str, t: int = 0, array_fmt: str = "zlib"
    ) -> dict:
        """Get a waveform using the T8 API.
        If no specific timestamp is provided, it returns the last available wave.
        """
        return self.__request(f"waves/{mach}/{point}/{pmode}/{t}?array_fmt={array_fmt}")

    def __list_spectra(
        self,
        mach: str,
        point: str,
        pmode: str,
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> dict:
        """List available spectra for a given machine, point, and processing mode."""
        base_url = f"spectra/{mach}/{point}/{pmode}"
        url = self.__build_url_with_timestamp_params(base_url, from_ts, to_ts)
        return self.__request(url)

    def __get_spectrum(
        self, mach: str, point: str, pmode: str, t: int = 0, array_fmt: str = "zlib"
    ) -> dict:
        """Get a spectrum using the T8 API.
        If no specific timestamp is provided, it returns the last available spectrum.
        """
        return self.__request(f"spectra/{mach}/{point}/{pmode}/{t}?array_fmt={array_fmt}")

    def __get_machine_trend(self, mach: str, array_fmt: str = "zlib") -> dict:
        """Get machine trend data."""
        return self.__request(f"trends/mach/{mach}?array_fmt={array_fmt}")

    def __get_point_trend(self, mach: str, point: str, array_fmt: str = "zlib") -> dict:
        """Get point trend data."""
        return self.__request(f"trends/point/{mach}/{point}?array_fmt={array_fmt}")

    def __get_proc_mode_trend(
        self, mach: str, point: str, pmode: str, array_fmt: str = "zlib"
    ) -> dict:
        """Get processing mode trend data."""
        return self.__request(f"trends/pmode/{mach}/{point}/{pmode}?array_fmt={array_fmt}")

    def __get_param_trend(self, mach: str, point: str, param: str, array_fmt: str = "zlib") -> dict:
        """Get parameter trend data."""
        return self.__request(f"trends/param/{mach}/{point}/{param}?array_fmt={array_fmt}")

    def list_proc_modes(self) -> list[dict]:
        """List available processing modes."""
        links = self.__list_wave_modes()
        items = links["_items"]
        pmodes = [parse_pmode_item(link) for link in items]
        return sorted(pmodes, key=lambda x: (x["machine"], x["point"], x["tag"]))

    def list_params(self) -> list[dict]:
        """List available parameters."""
        links = self.__list_params()
        items = links["_items"]
        params = [parse_pmode_item(link) for link in items]
        return sorted(params, key=lambda x: (x["machine"], x["point"], x["tag"]))

    def list_configs(self, from_ts: int | None = None, to_ts: int | None = None) -> list[str]:
        """List available configurations."""
        links = self.__list_configs(from_ts, to_ts)
        items = links["_items"]
        return [parse_link(link) for link in items]

    def get_config(self, conf: str) -> dict:
        """Get a specific configuration given its ID."""
        return self.__get_config(conf)

    def list_snapshots(
        self, mach: str, from_ts: int | None = None, to_ts: int | None = None
    ) -> list[int]:
        """List available snapshots for a given machine."""
        links = self.__list_snapshots(mach, from_ts, to_ts)
        items = links["_items"]
        return [int(parse_link(link)) for link in items]

    def get_snapshot(self, mach: str, t: int = 0) -> dict:
        """Get a snapshot using the T8 API.
        If no specific timestamp is provided, it returns the last available snapshot.
        """
        return self.__get_snapshot(mach, t)

    def list_wave_modes(self) -> list[str]:
        """List available processing modes."""
        links = self.__list_wave_modes()
        items = links["_items"]
        return [item["name"] for item in items]

    def list_waves(
        self,
        mach: str,
        point: str,
        pmode: str,
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> list[int]:
        """List available waves for a given machine, point, and processing mode."""
        links = self.__list_waves(mach, point, pmode, from_ts, to_ts)
        items = links["_items"]
        return [int(parse_link(link)) for link in items]

    def get_wave(
        self, mach: str, point: str, pmode: str, t: int = 0, array_fmt: str = "zint"
    ) -> Wave:
        """Get a waveform using the T8 API."""
        ret = self.__get_wave(mach, point, pmode, t, array_fmt)

        path = ":".join([mach, point, pmode])
        factor = ret.get("factor", 1.0)
        data = decode_array(ret["data"], array_fmt) * factor
        return Wave(
            path=path,
            speed=ret["speed"],
            snap_t=int(ret["snap_t"]),
            t=ret["t"],
            unit_id=ret["unit_id"],
            data=data,
            sample_rate=ret["sample_rate"],
        )

    def list_spectra(
        self,
        mach: str,
        point: str,
        pmode: str,
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> list[int]:
        """List available spectra for a given machine, point, and processing mode."""
        links = self.__list_spectra(mach, point, pmode, from_ts, to_ts)
        items = links["_items"]
        return [int(parse_link(link)) for link in items]

    def get_spectrum(
        self, mach: str, point: str, pmode: str, t: int = 0, array_fmt: str = "zint"
    ) -> Spectrum:
        """Get a spectrum using the T8 API."""
        ret = self.__get_spectrum(mach, point, pmode, t, array_fmt)

        path = ":".join([mach, point, pmode])
        factor = ret.get("factor", 1.0)
        data = decode_array(ret["data"], array_fmt) * factor
        return Spectrum(
            path=path,
            speed=ret["speed"],
            snap_t=int(ret["snap_t"]),
            t=ret["t"],
            unit_id=ret["unit_id"],
            min_freq=ret["min_freq"],
            max_freq=ret["max_freq"],
            data=data,
            window=ret["window"],
        )

    def get_machine_trend(self, mach: str) -> MachineTrend:
        """Get machine trend data."""
        data = self.__get_machine_trend(mach)
        fmt = "zlib"

        return MachineTrend(
            t=decode_array(data["t.I"], fmt, dtype=np.uint32),
            speed=decode_array(data["speed.f"], fmt),
            load=decode_array(data["load.f"], fmt),
            alarm=decode_array(data["alarm.B"], fmt, dtype=np.uint8),
            state=decode_array(data["state.B"], fmt, dtype=np.uint8),
            strategy=decode_array(data["strategy.B"], fmt, dtype=np.uint8),
        )

    def get_point_trend(self, mach: str, point: str) -> PointTrend:
        """Get point trend data."""
        data = self.__get_point_trend(mach, point)
        fmt = "zlib"

        return PointTrend(
            t=decode_array(data["t.I"], fmt, dtype=np.uint32),
            alarm=decode_array(data["alarm.B"], fmt, dtype=np.uint8),
            bias=decode_array(data["bias.f"], fmt),
        )

    def get_proc_mode_trend(self, mach: str, point: str, pmode: str) -> ProcModeTrend:
        """Get processing mode trend data."""
        data = self.__get_proc_mode_trend(mach, point, pmode)
        fmt = "zlib"

        return ProcModeTrend(
            t=decode_array(data["t.I"], fmt, dtype=np.uint32),
            alarm=decode_array(data["alarm.B"], fmt, dtype=np.uint8),
            mask=decode_array(data["mask.B"], fmt, dtype=np.uint8),
        )

    def get_param_trend(self, mach: str, point: str, param: str) -> ParamTrend:
        """Get parameter trend data."""
        data = self.__get_param_trend(mach, point, param)
        fmt = "zlib"

        return ParamTrend(
            t=decode_array(data["t.I"], fmt, dtype=np.uint32),
            value=decode_array(data["value.f"], fmt),
            alarm=decode_array(data["alarm.B"], fmt, dtype=np.uint8),
            unit=decode_array(data["unit.H"], fmt, dtype=np.uint16),
        )

    def get_status(self) -> Status:
        """Get the status of the T8 device."""
        status = self.__request("info/status")
        return Status(**status)

    def get_system_info(self) -> SystemInfo:
        """Get system information."""
        info = self.__request("info/system")
        return SystemInfo(**info)
