# TWave T8 API Client

A comprehensive Python client for interacting with the TWave T8 REST API.

The [T8](https://twave.io/en/solutions/t8) is an advanced vibration analysis and condition monitoring system designed for industrial applications.
This client library provides a pythonic interface to the T8 REST API, allowing you to access monitoring data,
perform operations, and integrate T8 functionality into your data analysis workflows.

> **Warning:** This project is a work in progress. While it aims to provide
> complete coverage of the T8 API, including data access and operations, some
> features may still be under development or subject to change.

## Features

- Complete T8 API coverage for data access and operations (in progress)
- Simple and intuitive object-oriented interface
- Command-line interface (CLI) for quick data retrieval and interaction
- Tools for accessing:
  - Snapshots
  - Waveforms
  - Spectra
  - Configuration data
  - Trend data (machines, points, parameters, processing modes)
- CSV and JSON export functionality for further data analysis

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for managing virtual environments and dependencies.

### Development Setup

1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/t8/t8-python-client.git
cd t8-python-client
```

2. Create a virtual environment using uv:

```bash
uv venv
```

### Running Tests and Quality Checks

Run the test suite:

```bash
uv run pytest
```

Run the linter to ensure code quality:

```bash
uv run ruff check
```

## Python API Usage

The library provides a simple interface for interacting with the T8 API:

```python
from t8_client.t8 import T8

# Initialize client
client = T8("http://localhost", "admin", "password")

# Get available parameters
params = client.list_params()

# Get spectrum data
spectrum = client.get_spectrum("Machine1", "Point1", "ProcMode1", timestamp)

# Get waveform data
wave = client.get_wave("Machine1", "Point1", "ProcMode1", timestamp)

# Get trend data
trend = client.get_param_trend("Machine1", "Point1", "Overall")
```

## Command Line Interface (CLI)

The package includes a powerful command-line client that provides quick access to T8 API functionality without writing code.

### Setting Up the CLI

To execute the CLI in the virtual environment, use:

```bash
uv run t8-cli
```

For easier access, create an alias in your shell configuration file (`.bashrc`, `.zshrc`, etc.):

```bash
alias t8-cli='uv run t8-cli'
```

### Authentication

All commands require connection parameters to access the T8 API. You can provide them in two ways:

1. Command-line options:

   ```bash
   t8-cli --host http://t8-server --user admin --passw password [command]
   ```

2. Environment variables (recommended):

   ```bash
   export T8_HOST=http://t8-server
   export T8_USER=admin
   export T8_PASSW=password
   ```

You can also use both methods together, taking into account that command-line options will override environment variables.

**Note:** The host URL must include the protocol (http or https) and the full base URL path.

### Available Commands

#### General Information

- List all parameters:

  ```bash
  t8-cli params
  ```

- List all processing modes:
  ```bash
  t8-cli proc_modes
  ```

#### Working with Snapshots

- List all snapshots for a machine:

  ```bash
  t8-cli snapshot list -M MachineTag
  ```

- Download a snapshot for a specific timestamp:
  ```bash
  t8-cli snapshot get -M MachineTag -t 2019-04-13T01:41:40Z
  ```
  If no timestamp is provided, the latest available snapshot will be downloaded.

#### Working with Spectra

- List available spectra timestamps:

  ```bash
  t8-cli spectrum list -M MachineTag -p PointTag -m PModeTag
  ```

- Download a spectrum in CSV format:
  ```bash
  t8-cli spectrum get -M MachineTag -p PointTag -m PModeTag -t 2019-04-13T01:38:16Z
  ```

#### Working with Waveforms

- List available waveform timestamps:

  ```bash
  t8-cli wave list -M MachineTag -p PointTag -m PModeTag
  ```

- Download a waveform in CSV format:
  ```bash
  t8-cli wave get -M MachineTag -p PointTag -m PModeTag -t 2019-04-13T01:38:16Z
  ```

#### Working with Trend Data

- Download machine trend data:

  ```bash
  t8-cli trend machine -M MachineTag
  ```

- Download point trend data:

  ```bash
  t8-cli trend point -M MachineTag -p PointTag
  ```

- Download processing mode trend data:

  ```bash
  t8-cli trend pmode -M MachineTag -p PointTag -m PModeTag
  ```

- Download parameter trend data:
  ```bash
  t8-cli trend param -M MachineTag -p PointTag --param ParamTag
  ```

## Output Format

Trends, waveforms and spectra are output in CSV format suitable for import into spreadsheets or data analysis tools.

Snapshots, configuration data and other data types are output in JSON format.

The output files are named according to the data type and identifiers used. By default, the files are saved in the current working directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
