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


@click.group()
@click.version_option(__version__, '-V', '--version', message=version_msg())
@click.option('-i', '--interactive', is_flag=True, show_default=True, default=False, help="Interactive mode." )
def main(interactive):
    """Renders the archetype
    """
    pass


@main.command()
@click.option('-c', '--checkout', type=str)
@click.option('-p', '--path', type=str)
@click.argument('owner')
@click.argument('name')
@click.argument('kind')
def register(checkout, path, owner, name, kind):
    """\b
    Registers a new project in the user's config
        OWNER       Github account/org that owns the repo
        NAME        Name of the repo
        KIND        Kind of repo (template/project)
    """
    click.echo('c: ' + checkout + ', p: ' + path)
    pass


@main.command()
def create():
    pass


@main.command()
def upgrade():
    pass

@main.command()
def preview():
    pass


@main.command()
def search():
    pass


@main.command()
def version():
    pass


@main.command()
def validate():
    pass


if __name__ == "__main__":
    main()