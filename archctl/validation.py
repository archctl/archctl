"""Set of validation functions for CLI and Interactive"""
import click

import archctl.github as gh
from archctl.user_config import p_repo_name_exists, t_repo_exists

confirm = ['yes', 'ye', 'y']
deny = ['no', 'n']


def ask_confirmation(msg):
    click.echo(msg)
    stop = input('Are you sure you want to continue? [y/N]: ').lower()
    while stop not in confirm + deny:
        click.echo('Please, answer Yes or No')
        stop = input('Are you sure you want to continue? [y/N]: ')

    if stop in deny:
        click.echo('Canceling command and exiting')
        exit(1)

    return True


def parse_template(template):
    template = template.split('@')

    if len(template) == 1:
        return [template[0], 'default']
    else:
        return template


def infer_kind(repo):
    if gh.has_templates(repo):
        return 'Template'
    else:
        return 'Project'


def validate_repo(value):
    if not gh.repo_exists(value):
        raise click.BadParameter('Repo must be either owner/name or a valid GitHub URL')

    return value


def validate_local_repo(repo):
    if not p_repo_name_exists(repo) and not t_repo_exists(repo):
        raise click.BadParameter('The indicated repo doesn\'t exist in the local config')


def validate_not_local_repo(repo):
    if p_repo_name_exists(repo) or t_repo_exists(repo):
        raise click.BadParameter('The indicated repo already exists in the local config')


def validate_local_repo_interactive(repo):
    if not p_repo_name_exists(repo) and not t_repo_exists(repo):
        return False

    return True


def validate_repos(repos):
    for repo in repos:
        if not gh.repo_exists(repo):
            raise click.BadParameter('Repo must be either owner/name or a valid GitHub URL')


def get_default_branch(repo):
    return gh.get_default_branch(repo)


def validate_branch(repo, branch):
    if not gh.branch_exists(repo, branch):
        raise click.BadParameter('There is no such branch in the given repo')


def validate_template_repo(t_repo):
    # Check the given repo exists and that it contains cookiecutter templates

    if not gh.repo_exists(t_repo):
        raise click.BadParameter('Repo must be either owner/name or a valid GitHub URL')
    elif infer_kind(t_repo) != 'Template':
        raise click.BadParameter('Couldn\'t find any templates in the given repo')


def validate_repo_name_available(repo):
    # Ask github API if given repo name is available (Doesn't already exist)
    if gh.repo_exists(repo):
        raise click.BadParameter('A project with the same name already exists in GitHub')


def validate_template(t_repo, template):

    template = parse_template(template)

    templates = []
    if template[1] == 'default':
        templates = gh.search_templates(t_repo)
    else:
        validate_branch(t_repo, template[1])
        templates = gh.search_templates(t_repo, template[1])

    if template[0] not in templates:
        raise click.BadParameter(f'Couldn\'t find template ({template}) in repository ({t_repo})')

    return templates[template[0]]


def validate_cookies(cookies, yes):
    # Check if the cookies file is a valid one
    if yes and cookies is None:
        raise click.BadParameter('When running in --yes-all mode, cookies are mandatory')


def validate_kind(repo, kind):
    inferred_kind = infer_kind(repo)
    if inferred_kind != kind:
        continue_ = ask_confirmation(f'Given kind of the repo ({kind}) doesn\'t match the inferred kind ({inferred_kind})')
        if not continue_:
            exit(1)


def validate_depth(depth):
    if depth <= 0 and not depth == -1:
        raise click.BadParameter('Depth must be a number higher than 0')


def validate_kind_interactive(repo, kind):
    if kind == 'Template':
        return kind == infer_kind(repo)

    return True


def validate_repo_interactive(repo):
    if not gh.repo_exists(repo):
        return False

    return True


def validate_register_repo_interactive(repo):

    # If the repo doesn't exist in GitHub.com
    if not gh.repo_exists(repo):
        return False

    # If the repo is already registered
    if t_repo_exists(repo) or p_repo_name_exists(repo):
        return False

    return True


def validate_repos_checkbox(repos):
    if len(repos) < 1:
        return False

    return True


def validate_t_repo_interactive(repo):
    if not gh.repo_exists(repo):
        return False

    templates = gh.search_templates(repo)
    if not templates:
        return False

    return True


def validate_repo_name_available_interactive(repo):
    """Ask github API if given repo name is available (Doesn't already exist)"""

    # If user is not logged in
    if not gh.check_user_auth():
        return False

    # If the given repo already exists in github.com
    if gh.get_repo_info(repo):
        return False

    return True


def validate_depth_interactive(value):
    if int(value) <= 0 and not int(value) == -1:
        return 'Depth must be a number higher than 0 or -1 to not impose a limit'

    return True


def validate_t_version_interactive(repo, template, t_version):
    # Check if the given version exists

    return True


def confirm_command_execution(ctx):
    click.echo('These are the values the command will be called with:')

    for name, value in ctx.params.items():
        param = next(param for param in ctx.to_info_dict()['command']['params'] if param["name"] == name)
        click.echo('\t' + str(param['opts']) + ': ' + str(value))

    ask_confirmation('')
