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
                                confirm_command_execution, get_default_branch,
                                infer_kind, validate_kind, validate_local_repo,
                                validate_not_local_repo)
import archctl.main as arch


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


@click.group()
@click.version_option(__version__, '-V', '--version', message=version_msg())
@click.option('-I', '--interactive', is_flag=True, default=False, callback=interactive_callback)
def main(interactive):
    """Renders the archetype
    """
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
        '-r', '--template-repo', required=True,
        help='Repo containing the template'
    ),
    click.option(
        '-t', '--template', required=True,
        help='Template to use'
    )
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@main.command()
@click.argument('repo')
@click.option(
    '-k', '--kind',
    type=click.Choice(['Project', 'Template'])
)
@click.option(
    '-b', '--branch',
    help="Default branch to chekout from when updating/previewing"
)
@add_options(common_options)
def register(repo, kind, branch, yes, verbose):
    """\b
    Registers a new project in the user's config
        REPO        Name (owner/name) or URL of the repo being added
    """

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    ctx = click.get_current_context()

    validate_repo(repo)
    validate_not_local_repo(repo)

    if kind is None:
        kind = infer_kind(repo)
        ctx.params['kind'] = kind
    else:
        validate_kind(repo, kind)

    if branch is None and kind == 'Project':
        branch = get_default_branch(repo)
        ctx.params['branch'] = branch
    elif branch is not None:
        validate_branch(repo, branch)

    # If running in --yes-all mode, skip any user confirmation
    if not yes:
        # Just do it
        confirm_command_execution(ctx)

    arch.register(repo, kind, branch)

    pass


@main.command()
def list():
    arch.list()
    pass


@main.command()
@click.argument('repo', required=True)
@add_options(common_options)
def delete(repo, yes, verbose):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    validate_local_repo(repo)

    # If running in --yes-all mode, skip any user confirmation
    if not yes:
        confirm_command_execution(click.get_current_context())

    arch.delete(repo)

    pass


@main.command()
@click.argument('repo')
@click.argument('new-repo')
@click.option('-b', '--branch')
@click.option(
    '-k', '--kind',
    type=click.Choice(['Project', 'Template'])
)
@add_options(common_options)
def modify(repo, new_repo, branch, kind, yes, verbose):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    ctx = click.get_current_context()

    validate_local_repo(repo)
    validate_repo(new_repo)
    validate_not_local_repo(new_repo)

    if kind is None:
        kind = infer_kind(new_repo)
        ctx.params['kind'] = kind
    else:
        validate_kind(new_repo, kind)

    if branch is None and kind == 'Project':
        branch = get_default_branch(new_repo)
        ctx.params['branch'] = branch
    elif branch is not None:
        validate_branch(new_repo, branch)

    # If running in --yes-all mode, skip any user confirmation
    if not yes:
        confirm_command_execution(ctx)

    arch.modify(repo, new_repo, kind, branch)

    pass


@main.command()
@click.argument('name')
@add_options(template_options)
@click.option(
    '-c', '--cookies',
    type=click.File(mode='r', errors='strict'),
    help="File containing the cookies that will be used when rendering the template"
)
@add_options(common_options)
def create(cookies, name, template_repo, template, verbose, yes):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    validate_repo_name_available(name)
    validate_template_repo(template_repo)
    path = validate_template(template_repo, template)
    validate_cookies(cookies, yes)

    # If running in --yes-all mode, skip any user confirmation
    if not yes:
        confirm_command_execution(click.get_current_context())

    arch.create(name, template_repo, template, path, cookies)

    pass


@main.command()
@click.argument('repos', nargs=-1, required=True)
@add_options(template_options)
@add_options(common_options)
def upgrade(repos, template_repo, template, verbose, yes):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    validate_repos(repos)
    validate_template_repo(template_repo)
    validate_template(template_repo, template)

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution(click.get_current_context())
    pass


@main.command()
@click.argument('repo')
@add_options(template_options)
@add_options(common_options)
def preview(repo, template, template_repo, verbose, yes):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    validate_repo(repo)
    validate_template_repo(template_repo)
    validate_template(template_repo, template)

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution(click.get_current_context())
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

    validate_template_repo(repo)
    validate_depth(depth)

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution(click.get_current_context())
    pass


@main.command()
@click.argument('repo')
@click.option(
    '-d', '--depth', type=int, default=5,
    help=""
)
@add_options(common_options)
def version(repo, depth, verbose, yes):

    setup_logger(stream_level='DEBUG' if verbose else 'INFO')

    validate_repo(repo)
    validate_depth(depth)

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print('Yeah')
    else:
        confirm_command_execution(click.get_current_context())
    pass


if __name__ == "__main__":
    main()
