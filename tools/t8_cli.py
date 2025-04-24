import json
import sys

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
        click.secho(f"Error connecting to T8 API: {e!s}", fg="red", err=True)
        sys.exit(1)


@click.command()
@click.pass_context
def info(ctx: Context) -> None:
    """Get the T8 device information"""
    client = ctx.obj["T8"]
    try:
        info = client.get_system_info()
    except Exception as e:
        click.secho(f"Error retrieving info: {e!s}", fg="red", err=True)
        sys.exit(1)

    print_system_info(info)


@click.command()
@click.pass_context
def license(ctx: Context) -> None:
    """Show the license information"""
    client = ctx.obj["T8"]
    try:
        info = client.get_system_info()
    except Exception as e:
        click.secho(f"Error retrieving info: {e!s}", fg="red", err=True)
        sys.exit(1)

    print_license(info.license, info.full_serial)


@click.command()
@click.pass_context
def status(ctx: Context) -> None:
    """Get the T8 status"""
    client = ctx.obj["T8"]
    try:
        status = client.get_status()
    except Exception as e:
        click.secho(f"Error retrieving status: {e!s}", fg="red", err=True)
        sys.exit(1)

    print_status(status)


@click.group()
@click.pass_context
def config(ctx: Context) -> None:
    """Manage configurations"""
    pass


@config.command(name="list")
@click.pass_context
def list_configs_cmd(ctx: Context) -> None:
    """List configuration IDs"""
    client = ctx.obj["T8"]
    try:
        configs = client.list_configs()
    except Exception as e:
        click.secho(f"Error listing configurations: {e!s}", fg="red", err=True)
        sys.exit(1)

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
        click.secho(e, fg="red", err=True)
        sys.exit(1)

    out_file = f"conf_{info.full_serial}_{config['uid']}.json"
    click.echo(f"Saving configuration to {out_file}")

    try:
        with open(out_file, "w") as f:
            json.dump(config, f, indent=4)
    except OSError as e:
        click.secho(f"Error saving file: {e!s}", fg="red", err=True)
        sys.exit(1)


@config.command(name="proc-modes")
@click.pass_context
def proc_modes(ctx: Context) -> None:
    """List all processing modes in the current configuration"""
    client = ctx.obj["T8"]
    try:
        pmodes = client.list_proc_modes()
        click.echo(tabulate(pmodes, headers="keys"))
    except Exception as e:
        click.secho(f"Error retrieving processing modes: {e!s}", fg="red", err=True)
        sys.exit(1)


@config.command(name="params")
@click.pass_context
def params(ctx: Context) -> None:
    """List all parameters in the current configuration"""
    client = ctx.obj["T8"]
    try:
        params = client.list_params()
        click.echo(tabulate(params, headers="keys"))
    except Exception as e:
        click.secho(f"Error retrieving parameters: {e!s}", fg="red", err=True)
        sys.exit(1)


@click.group()
@click.pass_context
def snapshot(ctx: Context) -> None:
    """Manage snapshots"""
    pass


@snapshot.command(name="list")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
def list_snapshots_cmd(ctx: Context, machine: str) -> None:
    """List snapshots"""
    client = ctx.obj["T8"]
    try:
        timestamps = client.list_snapshots(machine)
        for t in format_timestamps(timestamps):
            click.echo(t)
    except Exception as e:
        click.secho(f"Error listing snapshots: {e!s}", fg="red", err=True)
        sys.exit(1)


@snapshot.command(name="get")
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--time", "-t", help="Timestamp", default="1970-01-01T00:00:00Z")
def get_snapshot_cmd(ctx: Context, machine: str, time: str) -> None:
    """Get a snapshot at a specific timestamp."""
    try:
        t = parse_timestamp(time)
    except ValueError:
        click.secho(f"Invalid timestamp format: {time}", fg="red", err=True)
        sys.exit(1)

    client = ctx.obj["T8"]
    try:
        snap = client.get_snapshot(machine, t)
    except Exception as e:
        click.secho(f"Error retrieving snapshot: {e!s}", fg="red", err=True)
        sys.exit(1)

    print_snapshot(snap)
    out_file = f"ss_{machine}_{int(snap['t'])}.json"
    click.echo(f"Saving spectrum to {out_file}")

    try:
        with open(out_file, "w") as f:
            json.dump(snap, f, indent=4)
    except OSError as e:
        click.secho(f"Error saving file: {e!s}", fg="red", err=True)
        sys.exit(1)


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
def list_waves_cmd(ctx: Context, machine: str, point: str, pmode: str) -> None:
    """List waves"""
    client = ctx.obj["T8"]
    try:
        timestamps = client.list_waves(machine, point, pmode)
    except Exception as e:
        click.secho(f"Error listing waves: {e!s}", fg="red", err=True)
        sys.exit(1)

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
    except ValueError:
        click.secho(f"Invalid timestamp format: {time}", fg="red", err=True)
        sys.exit(1)

    client = ctx.obj["T8"]
    try:
        wave = client.get_wave(machine, point, pmode, t)
    except Exception as e:
        click.secho(f"Error retrieving wave: {e!s}", fg="red", err=True)
        sys.exit(1)

    print_wave(wave)
    duration = len(wave.data) / wave.sample_rate
    times = np.linspace(0, duration, len(wave.data), endpoint=False)

    out_file = f"wf_{machine}_{point}_{pmode}_{int(wave.snap_t)}.csv"
    click.echo(f"Saving waveform to {out_file}")
    header = "Time,Value"

    data = np.vstack((times, wave.data)).T
    try:
        np.savetxt(out_file, data, delimiter=",", fmt="%f", header=header)
    except OSError as e:
        click.secho(f"Error saving file: {e!s}", fg="red", err=True)
        sys.exit(1)


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
def list_spectra_cmd(ctx: Context, machine: str, point: str, pmode: str) -> None:
    """List spectra"""
    client = ctx.obj["T8"]
    try:
        timestamps = client.list_spectra(machine, point, pmode)
        for t in format_timestamps(timestamps):
            click.echo(t)
    except Exception as e:
        click.secho(f"Error listing spectra: {e!s}", fg="red", err=True)
        sys.exit(1)


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
    except ValueError:
        click.secho(f"Invalid timestamp format: {time}", fg="red", err=True)
        sys.exit(1)

    client = ctx.obj["T8"]
    try:
        sp = client.get_spectrum(machine, point, pmode, t)
    except Exception as e:
        click.secho(f"Error retrieving spectrum: {e!s}", fg="red", err=True)
        sys.exit(1)

    print_spectrum(sp)
    freqs = np.linspace(sp.min_freq, sp.max_freq, len(sp.data))

    out_file = f"sp_{machine}_{point}_{pmode}_{int(sp.snap_t)}.csv"
    click.echo(f"Saving spectrum to {out_file}")
    header = "Frequency,RMS"

    data = np.vstack((freqs, sp.data)).T
    try:
        np.savetxt(out_file, data, delimiter=",", fmt="%f", header=header)
    except OSError as e:
        click.secho(f"Error saving file: {e!s}", fg="red", err=True)
        sys.exit(1)


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
        click.secho(f"Error retrieving machine trend: {e!s}", fg="red", err=True)
        sys.exit(1)

    out_file = f"trend_mach_{machine}.csv"
    click.echo(f"Saving machine trend to {out_file}")

    data = np.vstack((trend.t, trend.speed, trend.load, trend.state, trend.alarm, trend.strategy)).T
    fmt = ["%d", "%f", "%f", "%d", "%d", "%d"]
    header = "Timestamp,Speed,Load,State,Alarm,Strategy"

    try:
        np.savetxt(out_file, data, delimiter=",", fmt=fmt, header=header)
    except OSError as e:
        click.secho(f"Error saving file: {e!s}", fg="red", err=True)
        sys.exit(1)


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
        click.secho(f"Error retrieving point trend: {e!s}", fg="red", err=True)
        sys.exit(1)

    out_file = f"trend_point_{machine}_{point}.csv"
    click.echo(f"Saving point trend to {out_file}")

    data = np.vstack((trend.t, trend.alarm, trend.bias)).T
    fmt = ["%d", "%d", "%f"]
    header = "Timestamp,Alarm,Bias"

    try:
        np.savetxt(out_file, data, delimiter=",", fmt=fmt, header=header)
    except OSError as e:
        click.secho(f"Error saving file: {e!s}", fg="red", err=True)
        sys.exit(1)


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
        click.secho(f"Error retrieving processing mode trend: {e!s}", fg="red", err=True)
        sys.exit(1)

    out_file = f"trend_pmode_{machine}_{point}_{pmode}.csv"
    click.echo(f"Saving processing mode trend to {out_file}")

    data = np.vstack((trend.t, trend.alarm, trend.mask)).T
    fmt = ["%d", "%d", "%d"]
    header = "Timestamp,Alarm,Mask"

    try:
        np.savetxt(out_file, data, delimiter=",", fmt=fmt, header=header)
    except OSError as e:
        click.secho(f"Error saving file: {e!s}", fg="red", err=True)
        sys.exit(1)


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
        click.secho(f"Error retrieving parameter trend: {e!s}", fg="red", err=True)
        sys.exit(1)

    out_file = f"trend_param_{machine}_{point}_{param}.csv"
    click.echo(f"Saving parameter trend to {out_file}")

    data = np.vstack((trend.t, trend.value, trend.alarm, trend.unit)).T
    fmt = ["%d", "%f", "%d", "%d"]
    header = "Timestamp,Value,Alarm,Unit"

    try:
        np.savetxt(out_file, data, delimiter=",", fmt=fmt, header=header)
    except OSError as e:
        click.secho(f"Error saving file: {e!s}", fg="red", err=True)
        sys.exit(1)


cli.add_command(info)
cli.add_command(license)
cli.add_command(status)
cli.add_command(config)
cli.add_command(snapshot)  # Add snapshot group command
cli.add_command(spectrum)  # Add spectrum group command
cli.add_command(wave)  # Add wave group command
cli.add_command(trend)  # Add trend group command


cli(auto_envvar_prefix="T8_")
