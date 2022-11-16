from abc import ABC, abstractmethod

# from InquirerPy import prompt

import archctl.commons as comm
from archctl.prompts import IPPrompt
from archctl.github import GHCli
from archctl.user_config import JSONConfig


class InteractivePrompt(ABC):

    @abstractmethod
    def interactive(self):
        """Returns a list of the """


class RegisterQuestions(InteractivePrompt):

    def __init__(self):
        self.prompt = IPPrompt()
        self.cli = GHCli()

    def interactive(self):
        """Interactive prompt flow for Register Command"""

        repo = comm.get_repo_dataclass(self.prompt.repo_text())

        self.cli.cw_repo = repo
        branches = [branch['name'] for branch in self.cli.list_branches()]

        repo.def_ref = self.prompt.branch_list(branches)
        kind = self.prompt.kind_list(repo)

        return {'repo': repo, 'kind': kind}


class DeleteQuestions(InteractivePrompt):

    def __init__(self):
        self.prompt = IPPrompt()
        self.uc = JSONConfig()

    def interactive(self):
        """Interactive prompt flow for Register Command"""

        repos = self.uc.project_repos() + self.uc.template_repos()
        repos = [repo.full_name for repo in repos]
        repo = comm.get_repo_dataclass(self.prompt.repo_list(repos))

        return {'repo': repo}
