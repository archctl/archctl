"""Main `archctl` CLI."""
import os
import sys

import click

from archctl import __version__


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
@click.option('-v', '--verbose', 'v', is_flag=True, default=False)
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
def register(yes, branch, repo, kind, v):
    """\b
    Registers a new project in the user's config
        REPO        Name (owner/name) or URL of the repo being added
        KIND        Kind of repo --> P for Project or T for Template
    """
    pass


@main.command()
@click.option('-v', '--verbose', 'v', is_flag=True, default=False)
@click.option(
    '-c', '--cookies',
    type=click.File(mode='r', errors='strict'),
    help="File containing the cookies that will be used when rendering the template"
)
@click.argument('name')
@click.argument('template')
def create(name, template, cookies, v):
    pass


@main.command()
@click.option('-v', '--verbose', 'v', is_flag=True, default=False)
@click.argument('repos', nargs=-1)
@click.argument('template')
def upgrade(repos, template, v):
    pass


@main.command()
@click.option('-v', '--verbose', 'v', is_flag=True, default=False)
@click.argument('repo')
@click.argument('template')
def preview(repo, template, v):
    pass


@main.command()
@click.option('-v', '--verbose', 'v', is_flag=True, default=False)
@click.argument('repo')
@click.option(
    '-d', '--depth', type=int, default=3,
    help="Number of commits to search for in each template/branch"
)
def search(repo, depth, v):
    pass


@main.command()
@click.option('-v', '--verbose', 'v', is_flag=True, default=False)
@click.argument('repo')
@click.option(
    '-d', '--depth', type=int, default=3,
    help=""
)
def version(repo, depth, v):
    pass


if __name__ == "__main__":
        main()