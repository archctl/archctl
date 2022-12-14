"""Main `archctl` CLI."""
import os
import sys

import click

from archctl import __version__
from archctl.logger import setup_logger
from archctl.validation import Validation
from archctl.github import GHCli
import archctl.utils as util
import archctl.main as archctl
import archctl.commons as comm
import archctl.commands as cmd


COMMANDS = {
    "register": cmd.Register,
    "list": cmd.List,
    "delete": cmd.Delete,
    "create": cmd.Create,
    "upgrade": cmd.Upgrade,
    "preview": cmd.Preview,
    "search": cmd.Search,
    # 'version': cmd.Version
}


common_options = [
    click.option(
        "-y",
        "--yes-all",
        "yes",
        is_flag=True,
        default=False,
        is_eager=True,
        help="No interaction, perform the command without asking",
    ),
    click.option("-v", "--verbose", is_flag=True, default=False, is_eager=True),
]

template_options = [click.argument("template-repo"), click.argument("template")]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def version_msg():
    """Return the Archctl version, location and Python powering it."""
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_version = sys.version
    return f"Archctl {__version__} from {location} (Python {python_version})"


@click.group()
@click.version_option(__version__, "-V", "--version", message=version_msg())
def main():
    """Renders the archetype"""


@main.command()
@click.option("-v", "--verbose", is_flag=True, default=False)
def it(verbose):

    setup_logger(stream_level="DEBUG" if verbose else "INFO")

    command = cmd.Commands().run()
    com = COMMANDS[command]

    com().run()


@main.command()
@click.argument("repo")
@click.option("-k", "--kind", type=click.Choice(["Project", "Template"]))
@click.option(
    "-b", "--branch", help="Default branch to chekout from when updating/previewing"
)
@add_options(common_options)
def register(repo, kind, branch, yes, verbose):
    """\b
    Registers a new project in the user's config
        REPO        Name (owner/name) or URL of the repo being added
    """

    setup_logger(stream_level="DEBUG" if verbose else "INFO")

    repo = comm.get_repo_dataclass(repo)

    cli = GHCli()
    cli.cw_repo = repo

    validator = Validation()

    validator.repo_exists_gh(repo)
    validator.repo_exists_uc(repo, False)

    if kind is None:
        if util.has_templates(cli):
            kind = "Template"
        else:
            kind = "Project"
    else:
        validator.kind(repo, kind)

    if branch is None:
        branch = cli.get_default_branch()
        repo.def_ref = branch
    else:
        validator.branch_exists_in_repo(repo, branch)

    # If running in --yes-all mode, skip any user confirmation
    if not yes:
        # Just do it
        validator.confirm_command_execution(
            repo=repo.full_name, kind=kind, branch=repo.def_ref
        )

    archctl.register(repo, kind)


@main.command()
def list():
    archctl.list()


@main.command()
@click.argument("repo", required=True)
@add_options(common_options)
def delete(repo, yes, verbose):

    setup_logger(stream_level="DEBUG" if verbose else "INFO")

    validator = Validation()

    repo = comm.get_repo_dataclass(repo)

    validator.repo_exists_uc(repo)

    # If running in --yes-all mode, skip any user confirmation
    if not yes:
        validator.confirm_command_execution(repo=repo.full_name)

    archctl.delete(repo)


@main.command()
@click.argument("name")
@add_options(template_options)
@click.option(
    "-c",
    "--cookies",
    type=click.File(mode="r", errors="strict"),
    help="File containing the cookies that will be used when rendering the template",
)
@add_options(common_options)
def create(cookies, name, template_repo, template, verbose, yes):

    setup_logger(stream_level="DEBUG" if verbose else "INFO")

    validator = Validation()
    cli = GHCli()

    repo = comm.get_repo_dataclass(name)
    t = comm.get_template_version_dataclass(template, template_repo)

    cli.cw_repo = template_repo
    if t.ref is None:
        t.ref = cli.get_default_branch()

    templates = util.search_templates(cli, t.ref)
    if templates:
        t.template.template_path = [
            temp.template_path
            for temp in templates
            if temp.template == t.template.template
        ][0]

    validator.repo_exists_gh(repo, False)
    validator.template(template)
    validator.cookies(cookies, yes)

    # If running in --yes-all mode, skip any user confirmation
    if not yes:
        validator.confirm_command_execution(
            name=repo.full_name,
            template=template.template,
            template_repo=template.template_repo.full_name,
            template_ref=template.template_version.ref,
        )

    archctl.create(repo, t, yes, cookies)


@main.command()
@click.argument("repos", nargs=-1, required=True)
@add_options(template_options)
@add_options(common_options)
def upgrade(repos, template_repo, template, verbose, yes):

    setup_logger(stream_level="DEBUG" if verbose else "INFO")

    validator = Validation()
    cli = GHCli()
    template_repo = comm.get_repo_dataclass(template_repo)

    repos = [
        comm.get_repo_dataclass(repo)
        for repo in repos
        if validator.repo_exists_gh(repo)
    ]
    t = comm.get_template_version_dataclass(template, template_repo)

    cli.cw_repo = template_repo
    templates = util.search_templates(cli, t.ref)
    if templates:
        t.template.template_path = [
            temp.template_path
            for temp in templates
            if temp.template == t.template.template
        ][0]

    if t.ref is None:
        t.ref = cli.get_default_branch()

    validator.template(template)

    # If running in --yes-all mode, skip any user confirmation
    if yes:
        # Just do it
        print("Yeah")
    else:
        names = [repo.full_name for repo in repos]
        validator.confirm_command_execution(
            repos=names,
            template=template.template,
            template_repo=template.template_repo,
            template_ref=template.template_version.ref,
        )

    archctl.upgrade(repos, t, yes)


@main.command()
@click.argument("repo")
@click.option(
    "-c",
    "--cookies",
    type=click.File(mode="r", errors="strict"),
    help="File containing the cookies that will be used when rendering the template",
)
@click.option(
    "-s",
    "--show-add",
    is_flag=True,
    default=False,
    help="Show the diffs for the added files, when not set, it just shows the names of the added files",
)
@add_options(template_options)
@add_options(common_options)
def preview(repo, template, template_repo, cookies, show_add, verbose, yes):

    setup_logger(stream_level="DEBUG" if verbose else "INFO")

    validator = Validation()
    cli = GHCli()

    repo = comm.get_repo_dataclass(repo)
    if repo.def_ref is None:
        cli.cw_repo = repo
        repo.def_ref = cli.get_default_branch()

    template_repo = comm.get_repo_dataclass(template_repo)
    t = comm.get_template_version_dataclass(template, template_repo)
    if t.ref is None:
        cli.cw_repo = template_repo
        t.ref = cli.get_default_branch()

    templates = util.search_templates(cli, t.ref)
    if templates:
        t.template.template_path = [
            temp.template_path
            for temp in templates
            if temp.template == t.template.template
        ][0]

    validator.repo_exists_gh(repo)
    validator.template(template)
    # validator.cookies(cookies, yes)

    # If running in --yes-all mode, skip any user confirmation
    if not yes:
        validator.confirm_command_execution(
            repos=repo.full_name,
            template=template.template,
            template_repo=template.template_repo.full_name,
            template_ref=template.template_version.ref,
        )

    archctl.preview(repo, t, show_add, yes, cookies)


@main.command()
@click.argument("repo")
@click.option(
    "-d",
    "--depth",
    type=int,
    default=3,
    help="Number of commits to search for in each template/branch",
)
@click.option("-t", "--template", help="")
@click.option("--tags", is_flag=True, default=False, help="")
@add_options(common_options)
def search(repo, depth, template, tags, verbose, yes):

    setup_logger(stream_level="DEBUG" if verbose else "INFO")

    validator = Validation()

    repo = comm.get_repo_dataclass(repo)

    if template is not None:
        template = comm.get_template_version_dataclass(template, repo)
        cli = GHCli()
        cli.cw_repo = repo
        templates = util.search_templates(cli, template.ref)
        if templates:
            template.template.template_path = [
                temp.template_path
                for temp in templates
                if temp.template == template.template.template
            ][0]
        if template.ref is None:
            template.ref = cli.get_default_branch()
        validator.template(template)

    validator.repo_exists_gh(repo)
    validator.depth(depth)

    # If running in --yes-all mode, skip any user confirmation
    if not yes:
        validator.confirm_command_execution(repo=repo.full_name, depth=depth)

    archctl.search(repo, depth, tags, template)


@main.command()
@click.argument("repo")
@click.option("-d", "--depth", type=int, default=5, help="")
@add_options(common_options)
def version(repo, depth, verbose, yes):

    setup_logger(stream_level="DEBUG" if verbose else "INFO")

    validator = Validation()

    repo = comm.get_repo_dataclass(repo)

    validator.repo_exists_gh(repo)
    validator.depth(depth)

    # If running in --yes-all mode, skip any user confirmation
    if not yes:
        validator.confirm_command_execution(repo=repo, depth=depth)

    # archctl.version(repo, depth)


if __name__ == "__main__":
    main()
