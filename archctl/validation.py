"""Set of validation functions for CLI and Interactive"""
import click

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


def is_repo(repo):
    # FILL WITH REPO VALIDATION LOGIC
    return True


def infer_kind(repo):
    # Get the repo content and Infer Type
    return 'Template'


def check_cookies(cookies_file):
    # Check if cookies configuration is valid
    return True


def validate_repo(ctx, param, value):
    if not is_repo(value):
        raise click.BadParameter('Repo must be either owner/name or a valid GitHub URL')

    return value


def validate_repos(ctx, param, value):
    for repo in value:
        if not is_repo(repo):
            raise click.BadParameter('Repo must be either owner/name or a valid GitHub URL')

    return value


def validate_branch(ctx, param, value):
    # Check if branch exists in repo
    # repo = ctx.params['repo']
    exists = True
    if not exists:
        raise click.BadParameter('There is no such branch in the given repo')

    return value


def validate_template_repo(ctx, param, value):
    # Check the given repo exists and that it contains cookiecutter templates
    if not is_repo(value):
        raise click.BadParameter('Repo must be either owner/name or a valid GitHub URL')
    elif infer_kind(value).lower() != 'template':
        raise click.BadParameter('Couldn\'t find any templates in the given repo')

    return value


def validate_repo_name_available(ctx, param, value):
    # Ask github API if given repo name is available (Doesn't already exist)
    available = True

    if not available:
        raise click.BadParameter('A project with the same name already exists in GitHub')

    return value


def validate_template(ctx, param, value):
    # Check if given template exists in the repo
    exists = True

    if not exists:
        raise click.BadParameter('Couldn\'t find template (' + value +
                                 ') in repository (' + ctx.params['templates_repo'] + ')')

    return value


def validate_cookies(ctx, param, value):
    # Check if the cookies file is a valid one
    valid_cookies = check_cookies(value)
    if ctx.params['yes'] and value is None:
        raise click.BadParameter('When running in --yes-all mode, cookies are mandatory')
    elif not valid_cookies:
        raise click.BadParameter('Problem found with cookies file')

    return value


def validate_depth(ctx, param, value):
    if value <= 0 and not value == -1:
        raise click.BadParameter('Depth must be a number higher than 0')

    return value


def validate_repo_interactive(repo):
    if not is_repo(repo):
        return 'Repo must be either owner/name or a valid GitHub URL'

    return True


def validate_repo_name_available_interactive(repo):
    # Ask github API if given repo name is available (Doesn't already exist)
    available = True

    if not available:
        return 'A project with the same name already exists in GitHub'

    return True


def validate_depth_interactive(value):
    if int(value) <= 0 and not int(value) == -1:
        return 'Depth must be a number higher than 0 or -1 to not impose a limit'

    return True


def validate_t_version_interactive(repo, template, t_version):
    # Check if the given version exists

    return True


def confirm_command_execution():
    click.echo('These are the values the command will be called with:')

    ctx = click.get_current_context()
    for name, value in ctx.params.items():
        param = next(param for param in ctx.to_info_dict()['command']['params'] if param["name"] == name)
        click.echo('\t' + str(param['opts']) + ': ' + str(value))

    ask_confirmation('')
