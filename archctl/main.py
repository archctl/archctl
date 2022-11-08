"""
Main entry point for the `archctl` command.
"""
import os

import logging
import click
from cookiecutter.main import cookiecutter as cc

import archctl.github as gh
import archctl.user_config as uc
import archctl.git_util as git_util
import archctl.validation as val


logger = logging.getLogger(__name__)

tmp_dir = '/tmp/.archctl/'


def register(repo, kind, branch=None):
    if kind == 'Project':
        if not uc.add_p_repo({'name': repo, 'def_branch': branch}):
            raise click.ClickException(f'Repo {repo} could not be added to local config')
    else:
        if not uc.add_t_repo(repo):
            raise click.ClickException(f'Repo {repo} could not be added to local config')

    click.echo(f'Repo {repo} added correctly to user config')


def list():
    click.echo('Project Repos:')
    for p_repo in uc.get_p_repos():
        name = p_repo['name']
        branch = p_repo['def_branch']
        click.echo(f'\t- {name} [ Default Branch: {branch} ]')

    click.echo('Template Repos:')
    for t_repo in uc.get_t_repos():
        click.echo(f'\t- {t_repo}')


def delete(repo):
    if not uc.delete_repo(repo):
        raise click.ClickException(f'Repo {repo} could not be deleted from local config')

    click.echo(f'Repo {repo} deleted from local config')


def modify(repo, new_repo, kind, branch=None):
    if kind == 'Project':
        new_repo = {'name': new_repo, 'def_branch': branch}

    if not uc.update_repo(repo, new_repo, kind):
        raise click.ClickException(f'Repo {repo} could not bet updated as {new_repo}')

    click.echo(f'Repo {repo} modified in local config for {new_repo}:')


def create(name, t_repo, t, path, yes, cookies=None):
    # Creation of the repo
    if gh.create_repo(name):

        # Clone the repo locally
        name = gh.parse_repo_name(name)
        tmp_repo = git_util.clone_repo(name, tmp_dir)

        # Get the variables ready for cookiecutter
        t_repo = gh.parse_repo_name(t_repo)
        t = val.parse_template(t)
        template = f'git@github.com:{t_repo[0]}/{t_repo[1]}.git'

        # Render the template
        cc(template=template, checkout=t[1], no_input=yes, overwrite_if_exists=True,
            output_dir=tmp_dir, config_file=cookies, directory=path)

        # Push the changes
        git_util.git_push_changes(tmp_repo, f'{tmp_dir}{name[1]}/.', 'Project creation and template render with Archctl')

        # Clean up the tmp dir
        os.system('rm -rf /tmp/.archctl/')
