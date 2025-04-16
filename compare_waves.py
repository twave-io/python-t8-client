import matplotlib.pyplot as plt
import numpy

files = [
    "wf_LP_Turbine_MAD31CY005_AM1_1555119736.csv",
    "wf_LP_Turbine_MAD31CY005_AM1_1555119736_b64.csv",
]


def read_wave_from_csv(file: str) -> tuple[numpy.ndarray, numpy.ndarray]:
    """Read a CSV file and return the data as a numpy array."""
    data = numpy.loadtxt(file, delimiter=",", skiprows=1)
    return data[:, 0], data[:, 1]  # Return time and amplitude columns


if __name__ == "__main__":
    # Read both waves and plot them

    for file in files:
        time, amplitude = read_wave_from_csv(file)
        plt.plot(time, amplitude, label=file)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Waveforms")
    plt.legend()
    plt.grid()
    plt.show()
