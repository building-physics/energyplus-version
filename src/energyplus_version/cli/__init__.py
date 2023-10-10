# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import click
import json
import jsonpatch
from ..version_22_1 import Upgrade
#from version_22_1 import Upgrade

from ..__about__ import __version__
#from __about__ import __version__

@click.command()
@click.argument('epjson', type=click.Path(exists=True)) #, help='epJSON file to upgrade')
@click.option('-d', '--downgradable', is_flag=True, show_default=True, default=False, help='Make the file downgradable.')
@click.option('-o', '--output', show_default=True, default='upgrade.epJSON', help='File name to write.')
def upgrade(epjson, downgradable, output):
    click.echo('Upgrade!')
    fp = open(epjson, 'r')
    # Need to catch any issues with reading the json
    epjson = json.load(fp)
    fp.close()
    try:
        version_string = list(epjson['Version'].values())[0]['version_identifier']
    except:
        click.echo('Failed to find version string, cannot proceed', err=True)
    print(version_string)
    # Need to do a proper lookup and do a plugin thing here
    upgrade = Upgrade()
    print(upgrade.describe())
    patch = upgrade.generate_patch(epjson)
    print(str(patch))
    jp = jsonpatch.JsonPatch(patch)
    new_epjson= jp.apply(epjson)
    # Need to set up the naming to mimic the current setup, just forge ahead for now
    fp = open(output, 'w')
    json.dump(new_epjson, fp, indent=4)
    fp.close()

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