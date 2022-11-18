"""Set of validation functions for CLI and Interactive"""
import click
import logging

from archctl.github import GHCli
from archctl.user_config import JSONConfig
import archctl.utils as util
import archctl.commons as comm

logger = logging.getLogger(__name__)

CONFIRM = ['yes', 'ye', 'y']
DENY = ['no', 'n']


class Validation():

    def __init__(self, interactive: bool = False):
        self.cli = GHCli()
        self.uc = JSONConfig()
        self.interactive = interactive

    def ask_confirmation(self, msg):
        click.echo(msg)
        stop = input('Are you sure you want to continue? [y/N]: ').lower()
        while stop not in CONFIRM + DENY:
            click.echo('Please, answer Yes or No')
            stop = input('Are you sure you want to continue? [y/N]: ')

        if stop in DENY:
            click.echo('Canceling command and exiting')
            exit(1)

        return True

    def repo_exists_gh(self, repo, exists: bool = True):
        """Given [repo, exists]"""
        self.cli.cw_repo = repo
        if exists != bool(self.cli.get_repo_info()):
            if self.interactive:
                return False
            else:
                if exists:
                    raise click.BadParameter('Repo doesn\'t exist in GitHub')
                else:
                    raise click.BadParameter('Repo already exists in Github')

        return True

    def repo_exists_uc(self, repo, exists: bool = True):
        """Returns a list of the """
        if exists != bool(self.uc.repo_exists(repo)):
            if self.interactive:
                return False
            else:
                if exists:
                    raise click.BadParameter('Repo doesn\'t exist in your local config')
                else:
                    raise click.BadParameter('Repo already exists in your local config')

        return True

    def template(self, t: comm.Template):
        """Returns a list of the """
        if t.template not in util.search_templates(t.template_repo, t.template_version.ref):
            if self.interactive:
                return False
            else:
                raise click.BadParameter('Template not found in the given repo')

        return True

    def branch_exists_in_repo(self, repo: comm.Repo, branch):
        """Returns a list of the """
        self.cli.cw_repo = repo
        if branch not in [b['name'] for b in self.cli.list_branches()]:
            if self.interactive:
                return False
            else:
                raise click.BadParameter('Branch doesn\'t exist in the repo')

        return True

    def kind(self, repo, kind):
        """Returns a list of the """
        if kind == 'Template' and not util.has_templates(repo):
            if self.interactive:
                return False
            else:
                raise click.BadParameter('No Cookiecutter templates found in repo')

        return True

    def depth(self, depth):
        """Returns a list of the """
        if depth <= 0 and not depth == -1:
            if self.interactive:
                return False
            else:
                raise click.BadParameter('Depth must be a number higher than 0')

        return True

    def cookies(self, cookies, yes):
        # Check if the cookies file is a valid one
        if yes and cookies is None:
            if self.interactive:
                return False
            else:
                raise click.BadParameter('When running in --yes-all mode, cookies are mandatory')

    def confirm_command_execution(self, **kwargs):
        mssg = '\nThese are the values the command will be called with:\n'
        for key, val in kwargs.items():
            key = ' '.join(key.split('_')).title()
            mssg += f'\n\t- {key}: {val}'

        logger.info(mssg)

        self.ask_confirmation('')


# class CLIValidation(Validation):

    # def confirm_command_execution(self, ctx):
    #     mssg = '\nThese are the values the command will be called with:\n'

    #     for name, value in ctx.params.items():
    #         param = next(param for param in ctx.to_info_dict()['command']['params'] if param["name"] == name)
    #         mssg += '\n\t' + str(param['opts']) + ': ' + str(value)

    #     logger.info(mssg)

    #     super().ask_confirmation('')


# class InteractiveValidation(Validation):

    # def confirm_command_execution(self, answers):
    #     mssg = '\nThese are the values the command will be called with:\n'
    #     for key, val in {k: v for k, v in answers.items() if v is not None}.items():
    #         key = ' '.join(key.split('_')).title()
    #         mssg += f'\n\t- {key}: {val}'

    #     logger.info(mssg)

    #     super().ask_confirmation('')
