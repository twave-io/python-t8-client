import sys

import click
import numpy as np
from click import Context
from tabulate import tabulate

from t8_client.models import Spectrum, Wave
from t8_client.t8 import T8
from t8_client.utils import format_timestamp, format_timestamps, parse_timestamp

DEFAULT_HOST = "http://localhost"

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "show_default": True,
}


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
def proc_modes(ctx: Context) -> None:
    """List processing modes"""
    client = ctx.obj["T8"]
    try:
        pmodes = client.list_proc_modes()
        click.echo(tabulate(pmodes, headers="keys"))
    except Exception as e:
        click.secho(f"Error retrieving processing modes: {e!s}", fg="red", err=True)
        sys.exit(1)


@click.command()
@click.pass_context
def params(ctx: Context) -> None:
    """List parameters"""
    client = ctx.obj["T8"]
    try:
        params = client.list_params()
        click.echo(tabulate(params, headers="keys"))
    except Exception as e:
        click.secho(f"Error retrieving parameters: {e!s}", fg="red", err=True)
        sys.exit(1)


@click.command()
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
def list_waves(ctx: Context, machine: str, point: str, pmode: str) -> None:
    """List waves"""
    client = ctx.obj["T8"]
    try:
        timestamps = client.list_waves(machine, point, pmode)
        for t in format_timestamps(timestamps):
            click.echo(t)
    except Exception as e:
        click.secho(f"Error listing waves: {e!s}", fg="red", err=True)
        sys.exit(1)


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


@click.command()
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
@click.option("--time", "-t", help="Timestamp", default="1970-01-01T00:00:00Z")
def get_wave(ctx: Context, machine: str, point: str, pmode: str, time: str) -> None:
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

    data = np.vstack((times, wave.data)).T
    try:
        np.savetxt(out_file, data, delimiter=",", fmt="%f")
    except OSError as e:
        click.secho(f"Error saving file: {e!s}", fg="red", err=True)
        sys.exit(1)


@click.command()
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
def list_spectra(ctx: Context, machine: str, point: str, pmode: str) -> None:
    """List spectra"""
    client = ctx.obj["T8"]
    try:
        timestamps = client.list_spectra(machine, point, pmode)
        for t in format_timestamps(timestamps):
            click.echo(t)
    except Exception as e:
        click.secho(f"Error listing spectra: {e!s}", fg="red", err=True)
        sys.exit(1)


@click.command()
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
@click.option("--time", "-t", help="Timestamp", default="1970-01-01T00:00:00Z")
def get_spectrum(ctx: Context, machine: str, point: str, pmode: str, time: str) -> None:
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

    data = np.vstack((freqs, sp.data)).T
    try:
        np.savetxt(out_file, data, delimiter=",", fmt="%f")
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


cli.add_command(proc_modes)
cli.add_command(params)
cli.add_command(list_waves)
cli.add_command(get_wave)
cli.add_command(list_spectra)
cli.add_command(get_spectrum)
cli.add_command(trend)  # Add the new trend group command


cli(auto_envvar_prefix="T8_")
