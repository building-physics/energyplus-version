# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import click
import json
import jsonpatch
import importlib
import energyplus_version as ev

from ..__about__ import __version__

@click.command()
@click.argument('epjson', type=click.Path(exists=True)) #, help='epJSON file to upgrade')
@click.option('-d', '--downgradable', is_flag=True, show_default=True, default=False, help='Make the file downgradable.')
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False, help='Operate verbosely and write out progress information.')
@click.option('-o', '--output', show_default=True, default='upgrade.epJSON', help='File name to write.')
def upgrade(epjson, downgradable, verbose, output):
    fp = open(epjson, 'r')
    # Need to catch any issues with reading the json
    epjson = json.load(fp)
    fp.close()
    try:
        version_string = list(epjson['Version'].values())[0]['version_identifier']
    except Exception as exc:
        click.echo('Failed to find version string (%s), cannot proceed' % str(exc), err=True)
    if verbose:
        click.echo('Attempting to upgrade from version %s.' % version_string)
    old_downgrade = epjson.pop('energyplus_version_downgrade', {})
    # Need to do a proper lookup and do a plugin thing here
    mod = importlib.import_module('energyplus_version.version_%s' % version_string.replace('.', '_'))
    upgrade = mod.Upgrade()
    if verbose:
        click.echo(upgrade.describe())
    patch = upgrade.generate_patch(epjson)
    if verbose:
        click.echo('Patch contains %d itactions' % len(patch))
    jp = jsonpatch.JsonPatch(patch)
    new_epjson= jp.apply(epjson)
    if verbose:
        click.echo('Patch succeessfully applied.')
    # Add in downgrade information if requested
    if downgradable:
        downpatch = jsonpatch.JsonPatch.from_diff(new_epjson, epjson)
        new_epjson['energyplus_version_downgrade'] = old_downgrade
        new_epjson['energyplus_version_downgrade'][version_string] = json.loads(downpatch.to_string())
        if verbose:
            click.echo('Downgrade information generated.')
    # Need to set up the naming to mimic the current setup, just forge ahead for now
    with open(output, 'w') as fp:
        # Need better checking for legal JSON here
        json.dump(new_epjson, fp, indent=4)

@click.command()
@click.argument('epjson', type=click.Path(exists=True)) #, help='epJSON file to downgrade')
@click.option('-o', '--output', show_default=True, default='downgrade.epJSON', help='File name to write.')
@click.option('-t', '--to', help='Version to downgrade to, defaults to one version back.')
def downgrade(epjson, output, to=None):
    fp = open(epjson, 'r')
    # Need to catch any issues with reading the json
    epjson = json.load(fp)
    fp.close()
    if 'energyplus_version_downgrade' in epjson:
        try:
            version_string = list(epjson['Version'].values())[0]['version_identifier']
        except Exception as exc:
            click.echo('Failed to find version string (%s), cannot proceed' % str(exc), err=True)
        version = ev.EnergyPlusVersion.from_string(version_string)
        if version is None:
            click.echo('Failed to process version string "%s", cannot proceed' % version_string, err=True)
        else:
            previous_version = str(version.previous())
            if previous_version in epjson['energyplus_version_downgrade']:
                jp = jsonpatch.JsonPatch(epjson['energyplus_version_downgrade'].pop(previous_version))
                new_epjson= jp.apply(epjson)
                # Need to set up the naming to mimic the current setup, just forge ahead for now
                fp = open(output, 'w')
                json.dump(new_epjson, fp, indent=4)
                fp.close()

@click.command()
@click.argument('version') #, help='version to describe')
def describe(version):
    # Need to do a proper lookup and do a plugin thing here
    mod = importlib.import_module('energyplus_version.version_%s' % version.replace('.', '_'))
    upgrade = mod.Upgrade()
    click.echo(upgrade.describe())

@click.group(context_settings={'help_option_names': ['-h', '--help']}, invoke_without_command=False)
@click.version_option(version=__version__, prog_name='energyplus_version')
@click.pass_context
def energyplus_version(ctx: click.Context):
    pass

energyplus_version.add_command(upgrade)
energyplus_version.add_command(downgrade)
energyplus_version.add_command(describe)