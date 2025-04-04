import sys

import click
import numpy as np
from tabulate import tabulate

from t8_client.t8 import T8

from .utils import format_timestamps, parse_timestamp

DEFAULT_HOST = "http://localhost"

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "show_default": True,
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option(
    "--host", help="T8 host", default=DEFAULT_HOST, envvar="T8_HOST", show_envvar=True
)
@click.option(
    "--user", help="Username", default="admin", envvar="T8_USER", show_envvar=True
)
@click.option("--passw", help="Password", envvar="T8_PASSW", show_envvar=True)
def cli(ctx, host, user, passw):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    ctx.obj["T8"] = T8(host, user, passw)


@click.command()
@click.pass_context
def proc_modes(ctx):
    """List processing modes"""
    client = ctx.obj["T8"]
    pmodes = client.list_proc_modes()
    print(tabulate(pmodes, headers="keys"))


@click.command()
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
def list_waves(ctx, machine, point, pmode):
    """List waves"""
    client = ctx.obj["T8"]
    timestamps = client.list_waves(machine, point, pmode)
    for t in format_timestamps(timestamps):
        print(t)


@click.command()
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
@click.option("--time", "-t", help="Timestamp", default="1970-01-01T00:00:00Z")
def get_wave(ctx, machine, point, pmode, time):
    """Get a wave at a specific timestamp and save it to a CSV file."""
    try:
        t = parse_timestamp(time)
    except ValueError:
        print("Invalid timestamp", file=sys.stderr)
        sys.exit(1)

    client = ctx.obj["T8"]
    wave = client.get_wave(machine, point, pmode, t)
    duration = len(wave.data) / wave.sample_rate
    print(f"Wave duration: {duration:.8f} s")
    print(f"Sample rate: {wave.sample_rate} Hz")
    print(f"Number of samples: {len(wave.data)}")
    times = np.linspace(0, duration, len(wave.data), endpoint=False)

    out_file = f"wf_{machine}_{point}_{pmode}_{int(wave.snap_t)}.csv"
    print(f"Saving waveform to {out_file}")

    data = np.vstack((times, wave.data)).T
    np.savetxt(out_file, data, delimiter=",", fmt="%f")


@click.command()
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
def list_spectra(ctx, machine, point, pmode):
    """List spectra"""
    client = ctx.obj["T8"]
    timestamps = client.list_spectra(machine, point, pmode)
    for t in format_timestamps(timestamps):
        print(t)


@click.command()
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
@click.option("--time", "-t", help="Timestamp", default="1970-01-01T00:00:00Z")
def get_spectrum(ctx, machine, point, pmode, time):
    """Get a spectrum at a specific timestamp and save it to a CSV file."""
    try:
        t = parse_timestamp(time)
    except ValueError:
        print("Invalid timestamp", file=sys.stderr)
        sys.exit(1)

    client = ctx.obj["T8"]
    sp = client.get_spectrum(machine, point, pmode, t)

    freqs = np.linspace(sp.min_freq, sp.max_freq, len(sp.data))

    out_file = f"sp_{machine}_{point}_{pmode}_{int(sp.snap_t)}.csv"
    print(f"Saving spectrum to {out_file}")

    data = np.vstack((freqs, sp.data)).T
    np.savetxt(out_file, data, delimiter=",", fmt="%f")


cli.add_command(proc_modes)
cli.add_command(list_waves)
cli.add_command(get_wave)
cli.add_command(list_spectra)
cli.add_command(get_spectrum)


cli(auto_envvar_prefix="T8_")
