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
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False, help='Operate verbosely and write out progress information.')
@click.option('-o', '--output', type=click.Path(writable=True), show_default=True, default='upgrade.epJSON', help='File name to write upgraded epJSON to.')
@click.option('-w', '--write-patch', type=click.Path(writable=True), show_default=False, default=None, help='Write the patch to the specified file.')
@click.option('--dry-run', is_flag=True, show_default=True, default=False, help='Generate the JSON patch but do not apply it.')
def upgrade(epjson, verbose, output, write_patch, dry_run):
    '''
    Uprade an epJSON file.
    '''
    fp = open(epjson, 'r')
    # Need to catch any issues with reading the json
    epjson = json.load(fp)
    fp.close()
    try:
        version_string = list(epjson['Version'].values())[0]['version_identifier']
    except Exception as exc:
        click.echo('Failed to find version string (%s), cannot proceed.' % str(exc), err=True)
        exit(1)
    if verbose:
        click.echo('Attempting to upgrade from version %s.' % version_string)
    # Need to do a proper lookup and do a plugin thing here
    mod = importlib.import_module('energyplus_version.version_%s' % version_string.replace('.', '_'))
    upgrade = mod.Upgrade()
    if verbose:
        click.echo(upgrade.describe())
    patch = upgrade.generate_patch(epjson)
    if write_patch is not None:
        with open(write_patch, 'w') as fp:
            json.dump(patch, fp, indent=4)
    if verbose:
        click.echo('Patch contains %d items.' % len(patch))
    jp = jsonpatch.JsonPatch(patch)
    if not dry_run:
        new_epjson= jp.apply(epjson)
        if verbose:
            click.echo('Patch successfully applied.')
        # Need to set up the naming to mimic the current setup, just forge ahead for now
        with open(output, 'w') as fp:
            # Need better checking for legal JSON here
            json.dump(new_epjson, fp, indent=4)
    else:
        if verbose:
            click.echo('Dry run: patch not applied.')

@click.command()
@click.argument('version') #, help='version to describe')
def describe(version):
    '''
    Describe the changes associated with a particular version.
    '''
    # Need to do a proper lookup and do a plugin thing here
    try:
        mod = importlib.import_module('energyplus_version.version_%s' % version.replace('.', '_'))
    except ModuleNotFoundError:
        click.echo('Failed to find version "%s", cannot proceed.' % version, err=True)
        exit(1)
    upgrade = mod.Upgrade()
    click.echo(upgrade.describe())

@click.group(context_settings={'help_option_names': ['-h', '--help']}, invoke_without_command=False)
@click.version_option(version=__version__, prog_name='energyplus_version')
@click.pass_context
def energyplus_version(ctx: click.Context):
    pass

energyplus_version.add_command(upgrade)
energyplus_version.add_command(describe)