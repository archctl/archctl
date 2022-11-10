"""
Main entry point for the `archctl` command.
"""
import os

import logging
import click

from cookiecutter.main import cookiecutter as cc

import archctl.github as gh
import archctl.user_config as uc
import archctl.git_utils as gu
import archctl.validation as val
import archctl.utils as utils


logger = logging.getLogger(__name__)

TMP_DIR = '/tmp/.archctl/'


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
        repo_path = f'{TMP_DIR}{name[1]}'
        tmp_repo = gu.clone_repo(name, repo_path)

        # Get the variables ready for cookiecutter
        t_repo = gh.parse_repo_name(t_repo)
        t = val.parse_template(t)
        template = f'git@github.com:{t_repo[0]}/{t_repo[1]}.git'

        # Render the template
        cc(template=template, checkout=t[1], no_input=yes, overwrite_if_exists=True,
            output_dir=repo_path, config_file=cookies, directory=path)

        # Push the changes
        gu.push_changes(tmp_repo, f'{repo_path}/.', 'Project creation and template render with Archctl')

        # Clean up the tmp dir
        os.system('rm -rf /tmp/.archctl/')


def upgrade(repos, t_repo, t, path, yes):

    # Get the variables ready for cookiecutter
    t_repo = gh.parse_repo_name(t_repo)
    t = val.parse_template(t)
    template = f'git@github.com:{t_repo[0]}/{t_repo[1]}.git'

    for repo in repos:

        # Set the working paths
        name = gh.parse_repo_name(repo['name'])
        tmp_render = f'{TMP_DIR}render-{name[1]}/'
        repo_path = f'{TMP_DIR}{name[1]}/'
        ignore_path = f'{repo_path}.archignore'

        # Clone the repo
        git_repo = gu.clone_repo(name, repo_path)
        branch = repo['branch']
        render_branch = 'archctl/upgrade-X'

        # Get the repo ready for the upgrade
        gu.checkout(git_repo, branch)
        gu.checkout(git_repo, render_branch)
        gu.publish_branch(git_repo, render_branch)

        # Render the template
        cc(template=template, checkout=t[1], no_input=yes, overwrite_if_exists=True,
            output_dir=tmp_render, directory=path)

        # Check if ignore file exists
        if not utils.exists(ignore_path):
            ignore_path = None

        # Move non-ignored files to the repo
        utils.move_dir(tmp_render, repo_path, ignore_path)

        # Push the changes
        gu.push_changes(git_repo, f'{repo_path}.', 'Project Update via Archctl')

        # Create a PR in the GH repo
        gh.create_pr(repo['name'], render_branch, branch, 'Upgrade No X via Archctl')

        # Clean up the tmp dir
        os.system('rm -rf /tmp/.archctl/')


def preview(repo, t_repo, t, path, yes):

    # Get the variables ready for cookiecutter
    t_repo = gh.parse_repo_name(t_repo)
    t = val.parse_template(t)
    template = f'git@github.com:{t_repo[0]}/{t_repo[1]}.git'

    # Set the working paths
    name = gh.parse_repo_name(repo['name'])
    tmp_render = f'{TMP_DIR}render-{name[1]}/'
    repo_path = f'{TMP_DIR}{name[1]}/'
    ignore_path = f'{repo_path}.archignore'
    branch = repo['branch']
    render_branch = 'archctl/preview'

    # Clone the repo
    git_repo = gu.clone_repo(name, repo_path)

    # Checkout to the existing branch the user specified the checkout from
    gu.checkout(git_repo, branch)
    # Checkout to the new local branch where the render will take place
    gu.checkout(git_repo, render_branch)

    # Render the template
    cc(template=template, checkout=t[1], no_input=yes, overwrite_if_exists=True,
        output_dir=tmp_render, directory=path)

    # Check if ignore file exists
    if not utils.exists(ignore_path):
        ignore_path = None

    # Move non-ignored files to the repo
    utils.move_dir(tmp_render, repo_path, ignore_path)

    # Generate diff between current branch (render) and user specified branch
    diff = gu.diff_branches(repo, branch)

    # Print additions
    print('Added files:')
    for addition in diff['A']:
        utils.print_diff(addition['name'], addition['diff'])

    # Print deletions
    print('Deleted files:')
    for addition in diff['D']:
        print(f'-{name}')

    # Print modifications
    print('Modified files:')
    for addition in diff['M']:
        utils.print_diff(addition['name'], addition['diff'])

    # Clean up the tmp dir
    os.system('rm -rf /tmp/.archctl/')
