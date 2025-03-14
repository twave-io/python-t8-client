import click

from t8_client.t8 import T8


def datetimes_to_str(datetimes):
    """Convert a list of datetimes to a list of ISO 8601 strings."""
    return [date.isoformat() for date in datetimes]


@click.group()
@click.pass_context
@click.option("--host", "-H", help="T8 host", default="http://localhost")
@click.option("--user", "-u", help="Username", default="admin")
@click.option("--passw", "-p", help="Password")
def cli(ctx, host, user, passw):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    ctx.obj["HOST"] = host
    ctx.obj["USER"] = user
    ctx.obj["PASSW"] = passw


@click.command()
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
def list_waves(ctx, machine, point, pmode):
    """List waves"""
    client = T8(ctx.obj["HOST"], ctx.obj["USER"], ctx.obj["PASSW"])
    waves = client.list_waves(machine, point, pmode)
    dates = datetimes_to_str(waves)

    for date in dates:
        print(date)


@click.command()
@click.pass_context
@click.option("--machine", "-M", help="Machine name", required=True)
@click.option("--point", "-p", help="Point name", required=True)
@click.option("--pmode", "-m", help="Processing mode", required=True)
@click.option("--t", help="Timestamp", default=0)
def get_wave(ctx, machine, point, pmode, t):
    """Get wave"""
    client = T8(ctx.obj["HOST"], ctx.obj["USER"], ctx.obj["PASSW"])
    wave = client.get_wave(machine, point, pmode, t)
    print(wave)


cli.add_command(list_waves)
cli.add_command(get_wave)
cli(auto_envvar_prefix="T8_CLIENT")
