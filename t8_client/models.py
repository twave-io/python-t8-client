from enum import IntEnum

from numpy.typing import NDArray
from pydantic import BaseModel


class LicenseFeature(BaseModel):
    """License feature information."""

    abbrev: str
    desc: str
    enabled: bool
    name: str
    number: int


class License(BaseModel):
    """License information."""

    changed_at: int
    expires_at: int
    features: list[LicenseFeature]


class SystemInfo(BaseModel):
    """System information."""

    serial: int
    full_serial: str
    model: str
    variant: str
    version: str
    revision: str
    hw_version: int
    board_model: str
    board_revision: int
    cpu_serial: int
    host: str
    enable_ntp: bool
    exp_module: str | None
    exp_serial: str | None
    installed_time: int
    license: License | None


class MountInfo(BaseModel):
    """Mount information."""

    device: str
    path: str
    total: int
    used: int
    volatile: bool


class Status(BaseModel):
    """System status information."""

    # Time
    timestamp: int
    up_time: float
    idle_time: float

    # Network
    host: str
    hw_addr: str
    ip_addr: str
    gateway: str
    prefix_length: int
    dhcp_enabled: bool

    # Storage
    data_mount: MountInfo
    rw_mount: MountInfo

    # Temperature and power
    board_temp: float
    cpu_temp: float
    vbat: float
    vinput: float
    fan_pwm: int


class Window(IntEnum):
    """Window types for spectrum analysis."""

    rect = 0
    hanning = 1
    hamming = 2
    blackman = 3

    def __str__(self) -> str:
        return self.name


class Wave(BaseModel):
    """Waveform data."""

    path: str  # Path to the waveform (machine:point:pmode)
    speed: float  # Rotation speed in Hz
    t: float  # Timestamp of the first sample in the waveform
    snap_t: int  # Timestamp of the snapshot
    unit_id: int  # Unit ID of the waveform data
    data: NDArray  # Waveform data as a NumPy array
    sample_rate: float  # Sample rate in Hz

    class Config:
        arbitrary_types_allowed = True


class Spectrum(BaseModel):
    """Spectrum data."""

    path: str  # Path to the spectrum (machine:point:pmode)
    speed: float  # Rotation speed in Hz
    t: float  # Timestamp of the first sample in the spectrum
    snap_t: int  # Timestamp of the snapshot
    unit_id: int  # Unit ID of the spectrum data
    data: NDArray  # Spectrum data as a NumPy array
    window: Window  # Window type
    max_freq: float  # Maximum frequency in the spectrum
    min_freq: float  # Minimum frequency in the spectrum

    class Config:
        arbitrary_types_allowed = True


class MachineTrend(BaseModel):
    """Machine trend data."""

    t: NDArray  # Timestamps
    speed: NDArray  # Speed array
    load: NDArray  # Load array
    alarm: NDArray  # Alarm array
    state: NDArray  # State array
    strategy: NDArray  # Strategy array

    class Config:
        arbitrary_types_allowed = True


class PointTrend(BaseModel):
    """Point trend data."""

    t: NDArray  # Timestamps
    alarm: NDArray  # Alarm array
    bias: NDArray  # Bias array

    class Config:
        arbitrary_types_allowed = True


class ProcModeTrend(BaseModel):
    """Processing mode trend data."""

    t: NDArray  # Timestamps
    alarm: NDArray  # Alarm array
    mask: NDArray  # Mask array

    class Config:
        arbitrary_types_allowed = True


class ParamTrend(BaseModel):
    """Parameter trend data."""

    t: NDArray  # Timestamps
    value: NDArray  # Parameter values
    alarm: NDArray  # Alarm array
    unit: NDArray  # Unit array

    class Config:
        arbitrary_types_allowed = True


class StateTrend(BaseModel):
    """State trend data."""

    t: NDArray  # Timestamps
    state: NDArray  # State array
    speed: NDArray  # Speed array
    load: NDArray  # Load array
    alarm: NDArray  # Alarm array
    strategy: NDArray  # Strategy array

    class Config:
        arbitrary_types_allowed = True
