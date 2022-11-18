from abc import ABC, abstractmethod
import archctl.main as archctl
from archctl.validation import Validation
import archctl.commons as comm
from archctl.prompts import IPPrompt
from archctl.github import GHCli
from archctl.user_config import JSONConfig
from archctl.utils import search_templates


class Command(ABC):

    @abstractmethod
    def run(self):
        """Returns a list of the """
        raise NotImplementedError


class Commands(Command):

    def __init__(self):
        self.prompt = IPPrompt()

    COMMANDS = ['register', 'list', 'delete', 'create', 'upgrade', 'preview', 'search', 'version']

    def run(self):
        """Returns a list of the """
        return self.prompt.command_list(self.COMMANDS)


class Register(Command):

    def __init__(self):
        self.prompt = IPPrompt()
        self.validator = Validation(True)
        self.cli = GHCli()

    def run(self):
        repo = comm.get_repo_dataclass(self.prompt.repo_text([1, 1]))

        self.cli.cw_repo = repo
        branches = [branch['name'] for branch in self.cli.list_branches()]

        repo.def_ref = self.prompt.branch_list(branches)
        kind = self.prompt.kind_list(repo)

        self.validator.confirm_command_execution(repo=repo.full_name, branch=repo.def_ref, kind=kind)

        archctl.register(repo, kind)


class List(Command):

    def run(self):
        archctl.list()


class Delete(Command):

    def __init__(self):
        self.prompt = IPPrompt()
        self.validator = Validation(True)
        self.uc = JSONConfig()

    def run(self):

        repos = [repo.full_name for repo in (self.uc.project_repos() + self.uc.template_repos())]
        repo = comm.get_repo_dataclass(self.prompt.repo_list(repos))

        self.validator.confirm_command_execution(repo=repo.full_name)

        archctl.delete(repo)


class Create(Command):

    def __init__(self):
        self.prompt = IPPrompt()
        self.validator = Validation(True)
        self.cli = GHCli()

    def run(self):

        repo = comm.get_repo_dataclass(self.prompt.repo_text([0, 0]))
        print('\nNow, please indicate the GH Repo that holds the Cookiecutter Template you wish to use')
        t_repo = comm.get_repo_dataclass(self.prompt.repo_text([1, -1]))

        self.cli.cw_repo = t_repo
        branches = [branch['name'] for branch in self.cli.list_branches()]

        ref = self.prompt.ref_list(branches)

        templates = search_templates(t_repo, ref)
        template = self.prompt.template_list(templates) + '@' + ref

        template = comm.get_template_dataclass(template, t_repo)
        template.template_path = search_templates(template.template_repo, template.template_version.ref)[template.template]

        if template.template_version is None:
            cli = GHCli()
            cli.cw_repo = template.template_repo
            ref = cli.get_repo_info()['default_branch']
            template.template_version = comm.get_template_version_dataclass(ref)
        
        self.validator.confirm_command_execution(project_name=repo.full_name, template_repo=template.template_repo.full_name,
                                                    template=template.template, version=template.template_version.full_name)

        archctl.create(repo, template, False)


class Upgrade(Command):

    def __init__(self):
        self.prompt = IPPrompt()
        self.validator = Validation(True)
        self.cli = GHCli()
        self.uc = JSONConfig()

    def __p_repo_manually(self):

        # Prompt the REPO
        repo = comm.get_repo_dataclass(self.prompt.repo_text([1, -1]))

        self.cli.cw_repo = repo
        branches = [branch['name'] for branch in self.cli.list_branches()]
        # Prompt the branch from the given REPO
        branch = self.prompt.branch_list(branches)
        # Add the given REPO and branch to the answer
        repo.def_ref = branch

        return repo

    # PROMPT FOR PROJECT REPOS
    def __p_repos_manually(self):

        print('Please enter one or more project repositories to upgrade!\n\t\t\t\t(One by One)')

        # Loop to prompt for a REPO and branch, one by one
        continue_ = True
        repos = []
        while continue_:
            repos.append(self.__p_repo_manually())
            # Prompt for continuation
            continue_ = self.prompt.confirm()

        return repos

    def __p_repos_from_config(self, repos):

        # Prompt to select which repos of the config user wants to upgrade
        repo_names = [repo.full_name for repo in repos]
        print(repo_names)
        selected_repos = self.prompt.repo_checkbox(repo_names)

        other = 'Other' in selected_repos

        # Get a list with all the info of the Project repos the user selected
        selected_repos = [repo for repo in repos if repo.full_name in selected_repos]

        # Prompt user to confirm if he wants to proceed with the stored config or modify it
        print('These are the default branches setup in local config:\n')
        for repo in selected_repos:
            print(f'\t- {repo.full_name} [ Default Branch: {repo.def_ref} ]')

        continue_ = self.prompt.confirm()
        if not continue_:  # If user says yes, PROJECT_REPOS holds all the info as a global var

            # When user indicates no, question which branch of the REPO the user
            # whishes to use in each REPO
            print('Please select the default branch for each of the selected projects')

            final_repos = []

            for repo in selected_repos:
                repo.def_ref = self.prompt.branch_text(repo)
                final_repos.append(repo)

            if other:
                final_repos += self.__p_repos_manually()

            return final_repos

        if other:
            selected_repos += self.__p_repos_manually()

        return selected_repos

    def __p_repos(self):
        """ Prompt user to select the projects to update from local config
            and optionally, add more manually
        """
        uc_repos = self.uc.project_repos()

        if uc_repos:  # If there are Project repos stored in the config
            return self.__p_repos_from_config(uc_repos)

        else:  # If there are no Project repos stored in the config
            return self.__p_repos_manually()

    def run(self):

        print('Please indicate the template you wish to use to Upgrade')

        t_repo = comm.get_repo_dataclass(self.prompt.repo_text([1, -1]))

        self.cli.cw_repo = t_repo
        branches = [branch['name'] for branch in self.cli.list_branches()]

        ref = self.prompt.ref_list(branches)

        templates = search_templates(t_repo, ref)
        template = self.prompt.template_list(templates) + '@' + ref

        template = comm.get_template_dataclass(template, t_repo)

        repos = self.__p_repos()

        archctl.upgrade(repos, template, False)
