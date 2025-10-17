import json
from collections.abc import Callable
from typing import Any

import click
import numpy as np
from click import Context
from tabulate import tabulate

from t8_client.models import License, MountInfo, Spectrum, Status, SystemInfo, Wave
from t8_client.t8 import T8
from t8_client.utils import format_timestamp, format_timestamps, parse_timestamp

DEFAULT_HOST = "http://localhost"

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "show_default": True,
}


def add_timestamp_options(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to add --start and --end timestamp options to a command."""
    func = click.option("--end", help="End timestamp (ISO 8601 format)", type=str)(func)
    return click.option(
        "--start",
        help="Start timestamp (ISO 8601 format)",
        type=str,
    )(func)


def parse_timestamp_options(
    start: str | None = None, end: str | None = None
) -> tuple[int | None, int | None]:
    """Parse and validate timestamp options, returning (start_ts, end_ts) tuple."""
    start_ts = None
    end_ts = None

    if start:
        try:
            start_ts = parse_timestamp(start)
        except ValueError as e:
            msg = f"Invalid start timestamp: {start}"
            raise click.BadParameter(msg) from e

    if end:
        try:
            end_ts = parse_timestamp(end)
        except ValueError as e:
            msg = f"Invalid end timestamp: {end}"
            raise click.BadParameter(msg) from e

    if start_ts is not None and end_ts is not None and start_ts >= end_ts:
        msg = "Start timestamp must be before end timestamp"
        raise click.ClickException(msg)

    return start_ts, end_ts


def save_wave_to_csv(wave: Wave, machine: str, point: str, pmode: str) -> str:
    """Save a wave to a CSV file and return the filename."""
    duration = len(wave.data) / wave.sample_rate
    times = np.linspace(0, duration, len(wave.data), endpoint=False)

    out_file = f"wf_{machine}_{point}_{pmode}_{int(wave.snap_t)}.csv"
    header = "Time,Value"

    data = np.vstack((times, wave.data)).T
    try:
        np.savetxt(out_file, data, delimiter=",", fmt="%f", header=header)
        return out_file
    except OSError as e:
        msg = f"Error saving file: {e!s}"
        raise click.ClickException(msg) from e


def save_spectrum_to_csv(spectrum: Spectrum, machine: str, point: str, pmode: str) -> str:
    """Save a spectrum to a CSV file and return the filename."""
    freqs = np.linspace(spectrum.min_freq, spectrum.max_freq, len(spectrum.data))

    out_file = f"sp_{machine}_{point}_{pmode}_{int(spectrum.snap_t)}.csv"
    header = "Frequency,RMS"

    data = np.vstack((freqs, spectrum.data)).T
    try:
        np.savetxt(out_file, data, delimiter=",", fmt="%f", header=header)
        return out_file
    except OSError as e:
        msg = f"Error saving file: {e!s}"
        raise click.ClickException(msg) from e


def print_system_info(info: SystemInfo) -> None:
    """Print system information."""
    click.echo("T8 System Information:")
    click.echo(f"Serial: \t{info.full_serial}")
    click.echo(f"Model: \t\t{info.model} {info.variant}")
    click.echo(f"Version: \t{info.version}")
    click.echo(f"Revision: \t{info.revision}")
    click.echo(f"HW Version: \t{info.hw_version}")
    click.echo(f"Host: \t\t{info.host}")

    if info.exp_module:
        click.echo(f"Exp Module: \t{info.exp_module} ({info.exp_serial})")


def print_mount_info(mount: MountInfo) -> None:
    """Print mount information."""
    click.echo(f"    Device: \t{mount.device}")
    click.echo(f"    Path: \t{mount.path}")
    click.echo(f"    Total: \t{mount.total} bytes")
    click.echo(f"    Used: \t{mount.used} bytes")
    click.echo(f"    Volatile: \t{mount.volatile}")


def print_status(status: Status) -> None:
    """Print status information."""
    click.echo("T8 Status:")
    click.echo(f"Time: \t\t{format_timestamp(status.timestamp)}")
    click.echo(f"Uptime: \t{status.up_time}")
    click.echo(f"Board Temp: \t{status.board_temp} °C")
    click.echo(f"CPU Temp: \t{status.cpu_temp} °C")
    click.echo(f"Input Voltage: \t{status.vinput} V")
    click.echo(f"Fan PWM: \t{status.fan_pwm}")
    click.echo(f"Host: \t\t{status.host}")
    click.echo(f"HW Addr: \t{status.hw_addr}")
    click.echo(f"IP Addr: \t{status.ip_addr}")
    click.echo(f"Gateway: \t{status.gateway}")
    click.echo(f"DHCP Enabled: \t{status.dhcp_enabled}")
    click.echo("Data Mount:")
    print_mount_info(status.data_mount)


def print_license(lic: License, serial: str) -> None:
    """Print license information."""
    print("License Information:")
    click.echo(f"Serial: \t{serial}")
    click.echo(f"Changed at: \t{format_timestamp(lic.changed_at)}")
    click.echo(f"Expires at: \t{format_timestamp(lic.expires_at)}")
    click.echo("\nFeatures:")

    features = [dict(feature) for feature in lic.features]
    features.sort(key=lambda x: x.get("number", 0))
    click.echo(tabulate(features, headers="keys"))


def print_snapshot(snap: dict) -> None:
    """Print snapshot information."""
    click.echo(f"Tag: \t\t{snap['tag']}")
    click.echo(f"Timestamp: \t{format_timestamp(snap['t'])}")
    click.echo(f"Conf ID: \t{snap['conf_id']}")
    click.echo(f"Speed: \t\t{snap['speed']} Hz")
    click.echo(f"State: \t\t{snap['state_id']}")


def print_wave(wave: Wave) -> None:
    """Print wave information."""
    duration = len(wave.data) / wave.sample_rate

    click.echo(f"Path: \t\t{wave.path}")
    click.echo(f"Speed: \t\t{wave.speed} Hz")
    click.echo(f"Timestamp: \t{format_timestamp(wave.t)}")
    click.echo(f"Snapshot: \t{format_timestamp(wave.snap_t)}")
    click.echo(f"Unit ID: \t{wave.unit_id}")
    click.echo(f"Sample rate: \t{wave.sample_rate} Hz")
    click.echo(f"Samples: \t{len(wave.data)}")
    click.echo(f"Duration: \t{duration:.3f} s")


def print_spectrum(sp: Spectrum) -> None:
    """Print spectrum information."""
    click.echo(f"Path: \t\t{sp.path}")
    click.echo(f"Speed: \t\t{sp.speed} Hz")
    click.echo(f"Timestamp: \t{format_timestamp(sp.t)} s")
    click.echo(f"Snapshot: \t{format_timestamp(sp.snap_t)} s")
    click.echo(f"Unit ID: \t{sp.unit_id}")
    click.echo(f"Max. freq: \t{sp.max_freq} Hz")
    click.echo(f"Min. freq: \t{sp.min_freq} Hz")
    click.echo(f"Window: \t{sp.window}")
    click.echo(f"Bins: \t\t{len(sp.data)}")


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option("--host", help="T8 host", default=DEFAULT_HOST, envvar="T8_HOST", show_envvar=True)
@click.option("--user", help="Username", default="admin", envvar="T8_USER", show_envvar=True)
@click.option("--passw", help="Password", envvar="T8_PASSW", show_envvar=True)
def cli(ctx: Context, host: str, user: str, passw: str) -> None:
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    try:
        ctx.obj["T8"] = T8(host, user, passw)
    except Exception as e:
        msg = f"Error connecting to T8 API: {e!s}"
        raise click.ClickException(msg) from e


@click.command()
@click.pass_context
def info(ctx: Context) -> None:
    """Get the T8 device information"""
    client = ctx.obj["T8"]
    try:
        info = client.get_system_info()
    except Exception as e:
        msg = f"Error retrieving info: {e!s}"
        raise click.ClickException(msg) from e

    print_system_info(info)


@click.command()
@click.pass_context
def license(ctx: Context) -> None:
    """Show the license information"""
    client = ctx.obj["T8"]
    try:
        info = client.get_system_info()
    except Exception as e:
        msg = f"Error retrieving info: {e!s}"
        raise click.ClickException(msg) from e

    print_license(info.license, info.full_serial)


@click.command()
@click.pass_context
def status(ctx: Context) -> None:
    """Get the T8 status"""
    client = ctx.obj["T8"]
    try:
        status = client.get_status()
    except Exception as e:
        msg = f"Error retrieving status: {e!s}"
        raise click.ClickException(msg) from e

    print_status(status)


@click.group()
@click.pass_context
def config(ctx: Context) -> None:
    """Manage configurations"""
    pass


@config.command(name="list")
@click.pass_context
@add_timestamp_options
def list_configs_cmd(ctx: Context, start: str, end: str) -> None:
    """List configuration IDs"""
    start_ts, end_ts = parse_timestamp_options(start, end)

    client = ctx.obj["T8"]
    try:
        configs = client.list_configs(start_ts, end_ts)
    except Exception as e:
        msg = f"Error listing configurations: {e!s}"
        raise click.ClickException(msg) from e

    for conf in configs:
        if conf != "0":
            click.echo(conf)


@config.command(name="get")
@click.pass_context
@click.option("--id", "-i", help="Configuration ID", default="0")
def get_config_cmd(ctx: Context, id: str) -> None:
    """Get a specific configuration given its ID and store it in a JSON file."""
    client = ctx.obj["T8"]

    try:
        info = client.get_system_info()
        config = client.get_config(id)
    except Exception as e:
        raise click.ClickException(str(e)) from e

    out_file = f"conf_{info.full_serial}_{config['uid']}.json"
    click.echo(f"Saving configuration to {out_file}")

    try:
        with open(out_file, "w") as f:
            json.dump(config, f, indent=4)
    except OSError as e:
        msg = f"Error saving file: {e!s}"
        raise click.ClickException(msg) from e


@config.command(name="proc-modes")
@click.pass_context
def proc_modes(ctx: Context) -> None:
    """List all processing modes in the current configuration"""
    client = ctx.obj["T8"]
    try:
        pmodes = client.list_proc_modes()
        click.echo(tabulate(pmodes, headers="keys"))
    except Exception as e:
        msg = f"Error retrieving processing modes: {e!s}"
        raise click.ClickException(msg) from e


@config.command(name="params")
@click.pass_context
def params(ctx: Context) -> None:
    """List all parameters in the current configuration"""
    client = ctx.obj["T8"]
    try:
        params = client.list_params()
        click.echo(tabulate(params, headers="keys"))
    except Exception as e:
        msg = f"Error retrieving parameters: {e!s}"
        raise click.ClickException(msg) from e


@click.group()
@click.pass_context
def snapshot(ctx: Context) -> None:
    """Manage snapshots"""
    pass


@snapshot.command(name="list")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@add_timestamp_options
def list_snapshots_cmd(ctx: Context, machine: str, start: str, end: str) -> None:
    """List snapshots"""
    start_ts, end_ts = parse_timestamp_options(start, end)

    client = ctx.obj["T8"]
    try:
        timestamps = client.list_snapshots(machine, start_ts, end_ts)
    except Exception as e:
        msg = f"Error listing snapshots: {e!s}"
        raise click.ClickException(msg) from e

    for t in format_timestamps(timestamps):
        click.echo(t)


@snapshot.command(name="get")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--time", "-t", help="Timestamp", default="1970-01-01T00:00:00Z")
def get_snapshot_cmd(ctx: Context, machine: str, time: str) -> None:
    """Get a snapshot at a specific timestamp."""
    try:
        t = parse_timestamp(time)
    except ValueError as e:
        msg = f"Invalid timestamp format: {time}"
        raise click.BadParameter(msg) from e

    client = ctx.obj["T8"]
    try:
        snap = client.get_snapshot(machine, t)
    except Exception as e:
        msg = f"Error retrieving snapshot: {e!s}"
        raise click.ClickException(msg) from e

    print_snapshot(snap)
    out_file = f"ss_{machine}_{int(snap['t'])}.json"
    click.echo(f"Saving spectrum to {out_file}")

    try:
        with open(out_file, "w") as f:
            json.dump(snap, f, indent=4)
    except OSError as e:
        msg = f"Error saving file: {e!s}"
        raise click.ClickException(msg) from e


@click.group()
@click.pass_context
def wave(ctx: Context) -> None:
    """Manage waveforms"""
    pass


@wave.command(name="list")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
@add_timestamp_options
def list_waves_cmd(
    ctx: Context, machine: str, point: str, pmode: str, start: str, end: str
) -> None:
    """List waves"""
    start_ts, end_ts = parse_timestamp_options(start, end)

    client = ctx.obj["T8"]
    try:
        timestamps = client.list_waves(machine, point, pmode, start_ts, end_ts)
    except Exception as e:
        msg = f"Error listing waves: {e!s}"
        raise click.ClickException(msg) from e

    for t in format_timestamps(timestamps):
        click.echo(t)


@wave.command(name="get")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
@click.option("--time", "-t", help="Timestamp", default="1970-01-01T00:00:00Z")
def get_wave_cmd(ctx: Context, machine: str, point: str, pmode: str, time: str) -> None:
    """Get a wave at a specific timestamp and save it to a CSV file."""
    try:
        t = parse_timestamp(time)
    except ValueError as e:
        msg = f"Invalid timestamp format: {time}"
        raise click.BadParameter(msg) from e

    client = ctx.obj["T8"]
    try:
        wave = client.get_wave(machine, point, pmode, t)
    except Exception as e:
        msg = f"Error retrieving wave: {e!s}"
        raise click.ClickException(msg) from e

    print_wave(wave)

    out_file = save_wave_to_csv(wave, machine, point, pmode)
    click.echo(f"Saving waveform to {out_file}")


@wave.command(name="download-range")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
@click.option("--start", "-s", help="Start date (ISO 8601 format)", required=True)
@click.option("--end", "-e", help="End date (ISO 8601 format)", required=True)
def download_waves_range_cmd(
    ctx: Context, machine: str, point: str, pmode: str, start: str, end: str
) -> None:
    """Download all waves between two dates and save them to CSV files."""
    start_timestamp, end_timestamp = parse_timestamp_options(start, end)

    client = ctx.obj["T8"]

    try:
        ts = client.list_waves(machine, point, pmode, start_timestamp, end_timestamp)
    except Exception as e:
        msg = f"Error listing waves: {e!s}"
        raise click.ClickException(msg) from e

    if not ts:
        click.echo(f"No waves found between {start} and {end}")
        return

    click.echo(f"Found {len(ts)} waves between {start} and {end}")

    downloaded_count = 0
    failed_count = 0

    for timestamp in ts:
        try:
            wave = client.get_wave(machine, point, pmode, timestamp)
            out_file = save_wave_to_csv(wave, machine, point, pmode)

            click.echo(f"Downloaded: {out_file}")
            downloaded_count += 1

        except Exception as e:
            click.echo(
                f"Error downloading wave at timestamp {timestamp}: {e!s}",
                err=True,
            )
            failed_count += 1
            continue

    click.echo(f"\nDownload complete: {downloaded_count} successful, {failed_count} failed")


@click.group()
@click.pass_context
def spectrum(ctx: Context) -> None:
    """Manage spectra"""
    pass


@spectrum.command(name="list")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
@add_timestamp_options
def list_spectra_cmd(
    ctx: Context, machine: str, point: str, pmode: str, start: str, end: str
) -> None:
    """List spectra"""
    start_ts, end_ts = parse_timestamp_options(start, end)

    client = ctx.obj["T8"]
    try:
        timestamps = client.list_spectra(machine, point, pmode, start_ts, end_ts)
    except Exception as e:
        msg = f"Error listing spectra: {e!s}"
        raise click.ClickException(msg) from e

    for t in format_timestamps(timestamps):
        click.echo(t)


@spectrum.command(name="get")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
@click.option("--time", "-t", help="Timestamp", default="1970-01-01T00:00:00Z")
def get_spectrum_cmd(ctx: Context, machine: str, point: str, pmode: str, time: str) -> None:
    """Get a spectrum at a specific timestamp and save it to a CSV file."""
    try:
        t = parse_timestamp(time)
    except ValueError as e:
        msg = f"Invalid timestamp format: {time}"
        raise click.BadParameter(msg) from e

    client = ctx.obj["T8"]
    try:
        sp = client.get_spectrum(machine, point, pmode, t)
    except Exception as e:
        msg = f"Error retrieving spectrum: {e!s}"
        raise click.ClickException(msg) from e

    print_spectrum(sp)

    out_file = save_spectrum_to_csv(sp, machine, point, pmode)
    click.echo(f"Saving spectrum to {out_file}")


@click.group()
@click.pass_context
def trend(ctx: Context) -> None:
    """Get trend data for various entities"""
    pass


@trend.command(name="machine")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
def machine_trend_cmd(ctx: Context, machine: str) -> None:
    """Get machine trend data and save it to a CSV file."""
    client = ctx.obj["T8"]
    try:
        trend = client.get_machine_trend(machine)
    except Exception as e:
        msg = f"Error retrieving machine trend: {e!s}"
        raise click.ClickException(msg) from e

    out_file = f"trend_mach_{machine}.csv"
    click.echo(f"Saving machine trend to {out_file}")

    data = np.vstack((trend.t, trend.speed, trend.load, trend.state, trend.alarm, trend.strategy)).T
    fmt = ["%d", "%f", "%f", "%d", "%d", "%d"]
    header = "Timestamp,Speed,Load,State,Alarm,Strategy"

    try:
        np.savetxt(out_file, data, delimiter=",", fmt=fmt, header=header)
    except OSError as e:
        msg = f"Error saving file: {e!s}"
        raise click.ClickException(msg) from e


@trend.command(name="point")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
def point_trend_cmd(ctx: Context, machine: str, point: str) -> None:
    """Get point trend data and save it to a CSV file."""
    client = ctx.obj["T8"]
    try:
        trend = client.get_point_trend(machine, point)
    except Exception as e:
        msg = f"Error retrieving point trend: {e!s}"
        raise click.ClickException(msg) from e

    out_file = f"trend_point_{machine}_{point}.csv"
    click.echo(f"Saving point trend to {out_file}")

    data = np.vstack((trend.t, trend.alarm, trend.bias)).T
    fmt = ["%d", "%d", "%f"]
    header = "Timestamp,Alarm,Bias"

    try:
        np.savetxt(out_file, data, delimiter=",", fmt=fmt, header=header)
    except OSError as e:
        msg = f"Error saving file: {e!s}"
        raise click.ClickException(msg) from e


@trend.command(name="pmode")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
def proc_mode_trend_cmd(ctx: Context, machine: str, point: str, pmode: str) -> None:
    """Get processing mode trend data and save it to a CSV file."""
    client = ctx.obj["T8"]
    try:
        trend = client.get_proc_mode_trend(machine, point, pmode)
    except Exception as e:
        msg = f"Error retrieving processing mode trend: {e!s}"
        raise click.ClickException(msg) from e

    out_file = f"trend_pmode_{machine}_{point}_{pmode}.csv"
    click.echo(f"Saving processing mode trend to {out_file}")

    data = np.vstack((trend.t, trend.alarm, trend.mask)).T
    fmt = ["%d", "%d", "%d"]
    header = "Timestamp,Alarm,Mask"

    try:
        np.savetxt(out_file, data, delimiter=",", fmt=fmt, header=header)
    except OSError as e:
        msg = f"Error saving file: {e!s}"
        raise click.ClickException(msg) from e


@trend.command(name="param")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--param", help="Parameter name", required=True)
def param_trend_cmd(ctx: Context, machine: str, point: str, param: str) -> None:
    """Get parameter trend data and save it to a CSV file."""
    client = ctx.obj["T8"]
    try:
        trend = client.get_param_trend(machine, point, param)
    except Exception as e:
        msg = f"Error retrieving parameter trend: {e!s}"
        raise click.ClickException(msg) from e

    out_file = f"trend_param_{machine}_{point}_{param}.csv"
    click.echo(f"Saving parameter trend to {out_file}")

    data = np.vstack((trend.t, trend.value, trend.alarm, trend.unit)).T
    fmt = ["%d", "%f", "%d", "%d"]
    header = "Timestamp,Value,Alarm,Unit"

    try:
        np.savetxt(out_file, data, delimiter=",", fmt=fmt, header=header)
    except OSError as e:
        msg = f"Error saving file: {e!s}"
        raise click.ClickException(msg) from e


cli.add_command(info)
cli.add_command(license)
cli.add_command(status)
cli.add_command(config)
cli.add_command(snapshot)  # Add snapshot group command
cli.add_command(spectrum)  # Add spectrum group command
cli.add_command(wave)  # Add wave group command
cli.add_command(trend)  # Add trend group command


cli(auto_envvar_prefix="T8_")
