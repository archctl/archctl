"""Main `archctl` CLI."""
import os
import sys

import click

from archctl import __version__
from archctl.logger import setup_logger

verbose = [
    click.option('-v', '--verbose', is_flag=True, default=False)
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def version_msg():
    """Return the Archctl version, location and Python powering it."""
    python_version = sys.version
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return f"Archctl {__version__} from {location} (Python {python_version})"


def is_repo(repo):
    # FILL WITH REPO VALIDATION LOGIC
    return True


def validate_repo(ctx, param, value):
    if is_repo(value):
        return value

    raise click.BadParameter("Repo must be either owner/name or a valid GitHub URL")


@click.group()
@click.version_option(__version__, '-V', '--version', message=version_msg())
def main():
    """Renders the archetype
    """
    pass


@main.command()
@click.option(
    '-y', '--yes-all', 'yes',
    is_flag=True, default=False,
    help="No interaction, perform action without asking"
)
@click.option(
    '-b', '--branch', type=str,
    help="Default branch to chekout from when updating/previewing"
)
@click.argument('repo', callback=validate_repo)
@click.argument('kind', type=click.Choice(['P', 'T'], case_sensitive=False))
@add_options(verbose)
def register(**kwargs):
    """\b
    Registers a new project in the user's config
        REPO        Name (owner/name) or URL of the repo being added
        KIND        Kind of repo --> P for Project or T for Template
    """
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')
    pass


@main.command()
@click.option(
    '-c', '--cookies',
    type=click.File(mode='r', errors='strict'),
    help="File containing the cookies that will be used when rendering the template"
)
@click.argument('name')
@click.argument('template')
@add_options(verbose)
def create(**kwargs):
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')
    pass


@main.command()
@click.argument('repos', nargs=-1)
@click.argument('template')
@add_options(verbose)
def upgrade(**kwargs):
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')
    pass


@main.command()
@click.argument('repo')
@click.argument('template')
@add_options(verbose)
def preview(**kwargs):
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')
    pass


@main.command()
@click.argument('repo')
@click.option(
    '-d', '--depth', type=int, default=3,
    help="Number of commits to search for in each template/branch"
)
@add_options(verbose)
def search(**kwargs):
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')
    pass


@main.command()
@click.argument('repo')
@click.option(
    '-d', '--depth', type=int, default=3,
    help=""
)
@add_options(verbose)
def version(**kwargs):
    setup_logger(stream_level='DEBUG' if verbose else 'INFO')
    pass


if __name__ == "__main__":
        main()