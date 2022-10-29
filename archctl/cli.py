"""Main `archctl` CLI."""
import os
import sys

import click

from archctl import __version__
from archctl.logger import setup_logger
from archctl.inquirer import interactive_prompt
from archctl.validation import validate_repo


def version_msg():
    """Return the Archctl version, location and Python powering it."""
    python_version = sys.version
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return f"Archctl {__version__} from {location} (Python {python_version})"


def interactive_callback(ctx, param, value):
    if value:
        interactive_prompt()
        exit(1)
    else:
        pass


def set_default_branch(repo):
    # Get default branch for repo
    branch = 'main'
    if click.get_current_context().params['yes']:
        click.echo('Setting ' + repo + '\'s default branch (' + branch + ') as default branch to checkout from when upgrading the template.')
    return branch


def confirm_command_execution():
    click.echo('These are the values the command will be called with:')

    ctx = click.get_current_context()
    for name, value in ctx.params.items():
        param = next(param for param in ctx.to_info_dict()['command']['params'] if param["name"] == name)
        click.echo('\t' + str(param['opts']) + ': ' + str(value))

    stop = input('Are you sure you want to continue? [y/N]: ')
    while stop not in ['Yes', 'YES', 'y', 'Y', 'No', 'N', 'no', 'n']:
        click.echo('Please, answer Yes or No')
        stop = input('Are you sure you want to continue? [y/N]: ')

    if stop in ['No', 'N', 'no', 'n']:
        click.echo('Canceling command and exiting')
        exit(0)


common_options = [
    click.option(
        '-y', '--yes-all', 'yes',
        is_flag=True, default=False,
        help="No interaction, perform the command without asking"
    ),
    click.option('-v', '--verbose', is_flag=True, default=False)
]

def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group()
@click.version_option(__version__, '-V', '--version', message=version_msg())
@click.option('-I', '--interactive', is_flag=True, default=False, callback=interactive_callback)
def main(interactive):
    """Renders the archetype
    """
    pass


@main.command()
@click.argument('repo', callback=validate_repo)
@click.argument('kind', type=click.Choice(['P', 'T'], case_sensitive=False))
@add_options(common_options)
@click.option(
    '-b', '--branch', type=str,
    default=lambda: set_default_branch(click.get_current_context().params['repo']),
    help="Default branch to chekout from when updating/previewing"
)
def register(repo, kind, branch, yes, verbose):
    """\b
    Registers a new project in the user's config
        REPO        Name (owner/name) or URL of the repo being added
        KIND        Kind of repo --> P for Project or T for Template
    """
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()
    
    pass


@main.command()
@click.argument('name')
@click.argument('template')
@click.option(
    '-c', '--cookies',
    type=click.File(mode='r', errors='strict'),
    help="File containing the cookies that will be used when rendering the template"
)
@add_options(common_options)
def create(cookies, name, template, verbose, yes):
    
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    if yes and cookies == None:
        raise click.UsageError('When running in --yes-all mode, cookies are mandatory')
    
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()
    
    pass


@main.command()
@click.argument('repos', nargs=-1, required=True)
@click.argument('template')
@add_options(common_options)
def upgrade(repos, template, verbose, yes):
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()
    pass


@main.command()
@click.argument('repo')
@click.argument('template')
@add_options(common_options)
def preview(repo, template, verbose, yes):
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()
    pass


@main.command()
@click.argument('repo')
@click.option(
    '-d', '--depth', type=int, default=3,
    help="Number of commits to search for in each template/branch"
)
@add_options(common_options)
def search(repo, depth, verbose, yes):
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()
    pass


@main.command()
@click.argument('repo')
@click.option(
    '-d', '--depth', type=int, default=5,
    help=""
)
@add_options(common_options)
def version(repo, depth,verbose, yes):
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()
    pass


if __name__ == "__main__":
        main()