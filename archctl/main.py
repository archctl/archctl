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
import archctl.utils as util


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
        tmp_repo = git_util.clone_repo(name, repo_path)

        # Get the variables ready for cookiecutter
        t_repo = gh.parse_repo_name(t_repo)
        t = val.parse_template(t)
        template = f'git@github.com:{t_repo[0]}/{t_repo[1]}.git'

        # Render the template
        cc(template=template, checkout=t[1], no_input=yes, overwrite_if_exists=True,
            output_dir=repo_path, config_file=cookies, directory=path)

        # Push the changes
        git_util.git_push_changes(tmp_repo, f'{repo_path}/.', 'Project creation and template render with Archctl')

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
                            PAth : {t.template_path}
                    ''')

        # Render the template
        cc(template=template, checkout=t[1], no_input=yes, overwrite_if_exists=True,
            output_dir=tmp_render, directory=path)

        # Check if ignore file exists
        if not util.exists(ignore_path):
            ignore_path = None

        # Move non-ignored files to the repo
        util.move_dir(tmp_render, repo_path, ignore_path)

        # Push the changes
        git_util.git_push_changes(git_repo, f'{repo_path}.', 'Project Update via Archctl')

        # Clean up the tmp dir
        os.system('rm -rf /tmp/.archctl/')
    
    except Exception as e:
        traceback.print_exc()
        logger.error(f'Exception: {str(e)}')
        os.system('rm -rf /tmp/.archctl/')


def search(t_repo: comm.Repo, depth, ref=None):
    """
        Searches for the available templates in the given template_repo and
        displays them along with depth versions.

        Ex:
            java:
                - java@v1
                - java@main/fb788fc
    """

    cli = GHCli()
    cli.cw_repo = t_repo

    templates = []

    if ref is None:
        ref = t_repo.def_ref
    
    templates = utils.search_templates(t_repo, ref)

    templates = [comm.Template(t, t_repo, p, None) for t, p in templates.items() ]

    versions = 

    for template in templates:


