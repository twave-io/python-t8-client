from enum import IntEnum

from numpy import ndarray
from pydantic import BaseModel


class Window(IntEnum):
    """Window types for spectrum analysis."""

    rect = 0
    hanning = 1
    hamming = 2
    blackman = 3

    def __str__(self):
        return self.name


class Wave(BaseModel):
    """Waveform data."""

    path: str  # Path to the waveform (machine:point:pmode)
    speed: float  # Rotation speed in Hz
    t: float  # Timestamp of the first sample in the waveform
    snap_t: int  # Timestamp of the snapshot
    unit_id: int  # Unit ID of the waveform data
    data: ndarray  # Waveform data as a NumPy array
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
    data: ndarray  # Spectrum data as a NumPy array
    window: Window  # Window type
    max_freq: float  # Maximum frequency in the spectrum
    min_freq: float  # Minimum frequency in the spectrum

    class Config:
        arbitrary_types_allowed = True
