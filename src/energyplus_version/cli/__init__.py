# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import click
import json

from ..__about__ import __version__

@click.command()
@click.argument('epjson', type=click.Path(exists=True)) #, help='epJSON file to upgrade')
@click.option('-d', '--downgradable', is_flag=True, show_default=True, default=False, help='Make the file downgradable.')
def upgrade(epjson, downgradable):
    click.echo('Upgrade!')
    fp = open(epjson, 'r')
    # Need to catch any issues with reading the json
    epjson = json.load(fp)
    fp.close()
    print(epjson['Version'])

@click.command()
def downgrade():
    click.echo('Downgrade')

@click.group(context_settings={'help_option_names': ['-h', '--help']}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name='energyplus_version')
@click.pass_context
def energyplus_version(ctx: click.Context):
    pass

energyplus_version.add_command(upgrade)
energyplus_version.add_command(downgrade)