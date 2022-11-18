"""
Main entry point for the `archctl` command.
"""
import logging
import os
import time

import click
from cookiecutter.main import cookiecutter as cc

import archctl.commons as comm
import archctl.git_utils as gu
from archctl.user_config import JSONConfig
import archctl.utils as utils
from archctl.github import GHCli
import traceback

import subprocess

logger = logging.getLogger(__name__)

TMP_DIR = '/tmp/.archctl/'


def register(repo: comm.Repo, kind):
    uc = JSONConfig()
    if kind == 'Project':
        if not uc.add_p_repo(repo):
            raise click.ClickException(f'Repo {repo.full_name} could not be added to local config')
    else:
        if not uc.add_t_repo(repo):
            raise click.ClickException(f'Repo {repo.full_name} could not be added to local config')

    click.echo(f'Repo {repo.full_name} added correctly to user config')


def list():
    uc = JSONConfig()
    click.echo('Project Repos:')
    p_repos = uc.project_repos()
    if p_repos:
        for p_repo in p_repos:
            click.echo(f'\t- {p_repo.full_name} [ Default Branch: {p_repo.def_ref} ]')

    t_repos = uc.template_repos()
    click.echo('Template Repos:')
    if t_repos:
        for t_repo in t_repos:
            click.echo(f'\t- {t_repo.full_name}')


def delete(repo: comm.Repo):
    uc = JSONConfig()
    if not uc.delete_repo(repo):
        raise click.ClickException(f'Repo {repo.full_name} could not be deleted from local config')

    click.echo(f'Repo {repo.full_name} deleted from local config')


def create(repo: comm.Repo, template: comm.Template, yes, cookies=None):

    cli = GHCli()
    cli.cw_repo = repo

    try:

        # Creation of the repo
        if cli.create_repo('Project creation via Archctl'):
            logger.debug(f'GH repo created: {repo.https_url}')

            # Clone the repo locally
            repo_path = f'{TMP_DIR}{repo.repo}'
            tmp_repo = gu.clone_repo(repo, repo_path)
            logger.debug(f'Repo cloned in {repo_path}')

            cc(template=template.template_repo.ssh_url, checkout=template.template_version.ref, no_input=yes,
                overwrite_if_exists=True, output_dir=repo_path, config_file=cookies, directory=template.template_path)
            logger.debug(f'Template rendered to {repo_path}')

            # Push the changes
            gu.push_changes(tmp_repo, f'{repo_path}/.', 'Project creation and template render with Archctl')
            logger.debug(f'Pushed the changes in {repo_path} to the remote repo')

            # Clean up the tmp dir
            os.system('rm -rf /tmp/.archctl/')
            logger.debug('Cleaned up the tmp directory')

    except Exception as e:
        traceback.print_exc()
        logger.error(f'Exception: {str(e)}')
        cmd = f'gh repo delete {repo.full_name}'
        subprocess.run(cmd.split())
        
        os.system('rm -rf /tmp/.archctl/')

def upgrade(repos, t: comm.Template, yes):

    cli = GHCli()

    for repo in repos:

        # Set the working paths
        cli.cw_repo = repo
        tmp_render = f'{TMP_DIR}render-{repo.repo}/'
        repo_path = f'{TMP_DIR}{repo.repo}/'
        ignore_path = f'{repo_path}.archignore'
        cookies = f'{TMP_DIR}cookiecutter.yaml'

        # Clone the repo
        git_repo = gu.clone_repo(repo, repo_path)
        branch = repo.def_ref
        render_branch = 'archctl/upgrade-X'

        # Get the repo ready for the upgrade
        gu.checkout(git_repo, branch)
        # Get the cookies for that repo
        utils.move_file(f'{repo_path}cookiecutter.yaml', cookies)
        gu.checkout(git_repo, render_branch)
        gu.publish_branch(git_repo, render_branch)

        # Render the template
        cc(template=t.template_repo.ssh_url, checkout=t.template_version.ref, no_input=yes,
            overwrite_if_exists=True, output_dir=repo_path, config_file=cookies, directory=t.template_path)

        # Check if ignore file exists
        if not utils.exists(ignore_path):
            ignore_path = None

        # Move non-ignored files to the repo
        utils.move_dir(tmp_render, repo_path, ignore_path)

        # Push the changes
        gu.push_changes(git_repo, f'{repo_path}.', 'Project Update via Archctl')

        # Create a PR in the GH repo
        cli.create_pr(render_branch, branch, 'Upgrade No X via Archctl')

        # Clean up the tmp dir
        os.system('rm -rf /tmp/.archctl/')


def preview(repo: comm.Repo, t: comm.Template, show_add, yes, cookies=None):

    uc = JSONConfig()

    cli = GHCli()
    cli.cw_repo = repo

    # Set the working paths
    tmp_render = f'{TMP_DIR}render-{repo.repo}/'
    repo_path = f'{TMP_DIR}{repo.repo}/'
    ignore_path = f'{repo_path}.archignore'
    branch = repo.def_ref
    render_branch = 'archctl/preview'

    try:

        # Clone the repo
        git_repo = gu.clone_repo(repo, repo_path)
        logger.debug(f'Cloned {repo.repo} in {repo_path}')

        # Checkout to the existing branch the user specified the checkout from
        gu.checkout(git_repo, branch)
        logger.debug(f'Checked out {repo.repo} to branch: {branch}')

        if cookies is None and utils.file_exists(f'{TMP_DIR}cookiecutter.yaml'):
            logger.debug(f'File with Cookies was found in the project\'s repo')
            cookies = f'{TMP_DIR}cookiecutter.yaml'
            utils.move_file(f'{repo_path}cookiecutter.yaml', cookies)
        elif cookies is not None:
            logger.debug(f'File with cookies was given by user')
            cookies = os.path.abspath(cookies.name)
        else:
            logger.debug(f'No Cookies given, prompting user')

        # Checkout to the new local branch where the render will take place
        gu.checkout(git_repo, render_branch)
        logger.debug(f'Checked out project to new branch to perform the render: {render_branch}')

        logger.debug(f'''Calling Cookiecutter with the following params:
                            Template Repo: {t.template_repo.full_name}
                            Checkout: {t.template_version.ref}
                            No Input: {yes}
                            Output Dir: {tmp_render}
                            Config File: {cookies}
                            Path to Template: {t.template_path}
                    ''')

        # Render the template
        cc(template=t.template_repo.ssh_url, checkout=t.template_version.ref, no_input=yes,
            overwrite_if_exists=True, output_dir=tmp_render, config_file=cookies, directory=t.template_path)

        # Check if ignore file exists
        if not utils.exists(ignore_path):
            ignore_path = None

        # Move non-ignored files to the repo
        tmp_render = str(utils.get_child_folder(tmp_render).absolute())
        utils.move_dir(tmp_render, repo_path, ignore_path)

        gu.commit_changes(git_repo, f'{repo_path}.', 'Preview via Archctl')

        # Generate diff between current branch (render) and user specified branch
        utils.print_diffs(gu.diff_branches(git_repo, branch), show_add)

        # Clean up the tmp dir
        os.system('rm -rf /tmp/.archctl/')
    
    except Exception as e:
        traceback.print_exc()
        logger.error(f'Exception: {str(e)}')
        os.system('rm -rf /tmp/.archctl/')


def search(t_repo, depth):
    """
        Searches for the available templates in the given template_repo and
        displays them along with depth versions.

        Ex:
            java:
                - java@v1
                - java@main/fb788fc
    """
