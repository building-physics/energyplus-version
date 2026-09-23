# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import importlib
import json

import click
import jsonpatch

from ..__about__ import __version__
from ..versioning import EnergyPlusVersion


def load_upgrade(version):
    module_name = 'energyplus_version.version_%s' % str(version).replace('.', '_')
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name != module_name:
            raise
        raise click.ClickException(
            'Failed to find an upgrade for version "%s".' % version
        ) from exc

    upgrade = module.Upgrade()
    if upgrade.from_version() != str(version):
        raise click.ClickException(
            'Upgrade module "%s" declares source version "%s".'
            % (module_name, upgrade.from_version())
        )
    return upgrade

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
    with open(epjson, 'r') as fp:
        epjson = json.load(fp)
    try:
        version_string = list(epjson['Version'].values())[0]['version_identifier']
    except (IndexError, KeyError, TypeError) as exc:
        raise click.ClickException(
            'Failed to find the EnergyPlus version identifier (%s).' % str(exc)
        ) from exc

    version = EnergyPlusVersion.from_energyplus_identifier(version_string)
    if version is None:
        raise click.ClickException(
            'Invalid EnergyPlus version identifier "%s".' % version_string
        )
    if verbose:
        click.echo('Attempting to upgrade from version %s.' % version)
    upgrade = load_upgrade(version)
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
    parsed_version = EnergyPlusVersion.from_string(version)
    if parsed_version is None:
        raise click.ClickException(
            'Invalid version "%s"; use a three-component version such as 23.2.0.' % version
        )
    upgrade = load_upgrade(parsed_version)
    click.echo(upgrade.describe())

@click.group(context_settings={'help_option_names': ['-h', '--help']}, invoke_without_command=False)
@click.version_option(version=__version__, prog_name='energyplus_version')
@click.pass_context
def energyplus_version(ctx: click.Context):
    pass

energyplus_version.add_command(upgrade)
energyplus_version.add_command(describe)
