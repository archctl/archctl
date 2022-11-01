"""Main `archctl` CLI."""
import os
import sys

import click

from archctl import __version__
from archctl.logger import setup_logger
from archctl.inquirer import interactive_prompt
from archctl.validation import (validate_template_repo, validate_template,
                                validate_repo, validate_branch,
                                validate_repo_name_available, validate_cookies,
                                validate_repos, validate_depth,
                                confirm_command_execution)


def version_msg():
    """Return the Archctl version, location and Python powering it."""
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_version = sys.version
    return f"Archctl {__version__} from {location} (Python {python_version})"


def interactive_callback(ctx, param, value):
    if value:
        interactive_prompt()
        exit(1)
    else:
        pass


common_options = [
    click.option(
        '-y', '--yes-all', 'yes',
        is_flag=True, default=False, is_eager=True,
        help="No interaction, perform the command without asking"
    ),
    click.option('-v', '--verbose', is_flag=True, default=False, is_eager=True)
]

template_options = [
    click.option(
        '-r', '--templates-repo', required=True,
        callback=validate_template_repo, help='Repo containing the template'
    ),
    click.option(
        '-t', '--template', required=True, callback=validate_template,
        help='Template to use'
    )
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
@click.option(
    '-k', '--kind', required=True,
    type=click.Choice(['Project', 'Template'], case_sensitive=False)
    )
@click.option(
    '-b', '--branch', type=str, callback=validate_branch, default='main',
    help="Default branch to chekout from when updating/previewing"
)
@add_options(common_options)
def register(repo, kind, branch, yes, verbose):
    """\b
    Registers a new project in the user's config
        REPO        Name (owner/name) or URL of the repo being added
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
@click.argument('name', callback=validate_repo_name_available)
@click.option(
    '-c', '--cookies',
    type=click.File(mode='r', errors='strict'),
    callback=validate_cookies,
    help="File containing the cookies that will be used when rendering the template"
)
@add_options(template_options)
@add_options(common_options)
def create(cookies, name, templates_repo, template, verbose, yes):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()

    pass


@main.command()
@click.argument('repos', nargs=-1, callback=validate_repos, required=True)
@add_options(template_options)
@add_options(common_options)
def upgrade(repos, templates_repo, template, verbose, yes):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()
    pass


@main.command()
@click.argument('repo', callback=validate_repo)
@add_options(template_options)
@add_options(common_options)
def preview(repo, template, verbose, yes):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()
    pass


@main.command()
@click.argument('repo', callback=validate_repo)
@click.option(
    '-d', '--depth', type=int, default=3,
    callback=validate_depth,
    help="Number of commits to search for in each template/branch"
)
@add_options(common_options)
def search(repo, depth, verbose, yes):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()
    pass


@main.command()
@click.argument('repo', callback=validate_repo)
@click.option(
    '-d', '--depth', type=int, default=5,
    callback=validate_depth,
    help=""
)
@add_options(common_options)
def version(repo, depth, verbose, yes):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution()
    pass


if __name__ == "__main__":
    main()
