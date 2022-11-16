"""
Main entry point for the `archctl` command.
"""
import logging
import os

import click
from cookiecutter.main import cookiecutter as cc

import archctl.commons as comm
import archctl.git_utils as gu
from archctl.user_config import JSONConfig
import archctl.utils as utils
from archctl.github import GHCli

logger = logging.getLogger(__name__)

TMP_DIR = '/tmp/.archctl/'


class Archctl():

    def __init__(self):
        self.uc = JSONConfig()

    def register(self, repo: comm.Repo, kind):
        if kind == 'Project':
            if not self.uc.add_p_repo(repo):
                raise click.ClickException(f'Repo {repo.full_name} could not be added to local config')
        else:
            if not self.uc.add_t_repo(repo):
                raise click.ClickException(f'Repo {repo.full_name} could not be added to local config')

        click.echo(f'Repo {repo.full_name} added correctly to user config')

    def list(self):
        click.echo('Project Repos:')
        p_repos = self.uc.project_repos()
        if p_repos:
            for p_repo in p_repos:
                click.echo(f'\t- {p_repo.full_name} [ Default Branch: {p_repo.def_ref} ]')

        t_repos = self.uc.template_repos()
        click.echo('Template Repos:')
        if t_repos:
            for t_repo in t_repos:
                click.echo(f'\t- {t_repo.full_name}')

    def delete(self, repo: comm.Repo):
        if not self.uc.delete_repo(repo):
            raise click.ClickException(f'Repo {repo.full_name} could not be deleted from local config')

        click.echo(f'Repo {repo.full_name} deleted from local config')

    def create(self, repo: comm.Repo, template: comm.Template, yes, cookies=None):

        cli = GHCli()
        cli.cw_repo = repo

        # Creation of the repo
        if cli.create_repo('Project creation via Archctl'):

            # Clone the repo locally
            repo_path = f'{TMP_DIR}{repo.repo}'
            tmp_repo = gu.clone_repo(repo, repo_path)

            # Render the template
            cc(template=template.template_repo.ssh_url, checkout=template.template_version.ref, no_input=yes,
                overwrite_if_exists=True, output_dir=repo_path, config_file=cookies, directory=template.template_path)

            # Push the changes
            gu.push_changes(tmp_repo, f'{repo_path}/.', 'Project creation and template render with Archctl')

            # Clean up the tmp dir
            os.system('rm -rf /tmp/.archctl/')

    def upgrade(self, repos, t_repo, t, path, yes):

        cli = GHCli()

        # Get the variables ready for cookiecutter
        t = comm.get_template_dataclass(t, t_repo)

        for repo in repos:

            # Set the working paths
            cli.cw_repo = repo['name']
            tmp_render = f'{TMP_DIR}render-{cli.cw_repo.repo}/'
            repo_path = f'{TMP_DIR}{cli.cw_repo.repo}/'
            ignore_path = f'{repo_path}.archignore'

            # Clone the repo
            git_repo = gu.clone_repo(cli.cw_repo, repo_path)
            branch = repo['branch']
            render_branch = 'archctl/upgrade-X'

            # Get the repo ready for the upgrade
            gu.checkout(git_repo, branch)
            gu.checkout(git_repo, render_branch)
            gu.publish_branch(git_repo, render_branch)

            # Render the template
            cc(template=t.template_repo.ssh_url, checkout=t.template_version.ref, no_input=yes,
                overwrite_if_exists=True, output_dir=repo_path, directory=path)

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

    def preview(self, repo, t_repo, t, path, yes):

        cli = GHCli()
        cli.cw_repo = repo

        # Get the variables ready for cookiecutter
        t = comm.get_template_dataclass(t, t_repo)

        # Set the working paths
        tmp_render = f'{TMP_DIR}render-{cli.cw_repo.repo}/'
        repo_path = f'{TMP_DIR}{cli.cw_repo.repo}/'
        ignore_path = f'{repo_path}.archignore'
        branch = repo['branch']
        render_branch = 'archctl/preview'

        # Clone the repo
        git_repo = gu.clone_repo(cli.cw_repo, repo_path)

        # Checkout to the existing branch the user specified the checkout from
        gu.checkout(git_repo, branch)
        # Checkout to the new local branch where the render will take place
        gu.checkout(git_repo, render_branch)

        # Render the template
        cc(template=t.template_repo.ssh_url, checkout=t.template_version.ref, no_input=yes,
            overwrite_if_exists=True, output_dir=tmp_render, directory=path)

        # Check if ignore file exists
        if not utils.exists(ignore_path):
            ignore_path = None

        # Move non-ignored files to the repo
        utils.move_dir(tmp_render, repo_path, ignore_path)

        # Generate diff between current branch (render) and user specified branch
        utils.print_diffs(gu.diff_branches(repo, branch))

        # Clean up the tmp dir
        os.system('rm -rf /tmp/.archctl/')

    def search(self, t_repo, depth):
        """
            Searches for the available templates in the given template_repo and
            displays them along with depth versions.

            Ex:
                java:
                    - java@v1
                    - java@main/fb788fc
        """
        
