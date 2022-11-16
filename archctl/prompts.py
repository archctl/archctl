from InquirerPy import inquirer
from archctl.validation import InteractiveValidation
from abc import ABC, abstractmethod
import archctl.commons as comm
from dataclasses import dataclass


@dataclass
class Checks:
    exists_gh: bool
    exists_uc: bool


class ArchctlPrompt(ABC):
    QUESTIONS = {
        'repo_text': 'Name of the repository (owner/name or URL)',
        'repo_list': 'Select a repository from the list',
        'kind_list': 'Select the kind of repository from the list',
        'branch_text': 'Name of the branch',
        'branch_list': 'Select the repo\'s branch',
        'template_list': 'Select the name of template',
        'template_version_text': 'Version of the template to use'
    }

    @abstractmethod
    def repo_text(self):
        raise NotImplementedError

    @abstractmethod
    def repo_list(self, choices):
        raise NotImplementedError

    @abstractmethod
    def kind_list(self, choices):
        raise NotImplementedError

    @abstractmethod
    def branch_text(self, choices):
        raise NotImplementedError

    @abstractmethod
    def branch_list(self, choices):
        raise NotImplementedError

    @abstractmethod
    def template_list(self, choices):
        raise NotImplementedError


class IPPrompt(ArchctlPrompt):

    def __init__(self):
        self.validator = InteractiveValidation()

    def __val_reg_repo(self, input):
        input = comm.get_repo_dataclass(input)
        return (self.validator.repo_exists_gh(input) and self.validator.repo_exists_uc(input, False))

    def repo_text(self):
        return inquirer.text(
            message=super().QUESTIONS['repo_text'],
            validate=self.__val_reg_repo
        ).execute()

    def kind_list(self, repo):
        return inquirer.select(
            message=super().QUESTIONS['kind_list'],
            choices=['Template', 'Project'],
            validate=lambda kind: self.validator.kind(repo, kind),
            invalid_message='Given repo doesn\'t contain any Cookiecutter Templates'
        ).execute()

    def branch_text(self, choices):
        raise NotImplementedError

    def branch_list(self, choices):
        return inquirer.select(
            message=super().QUESTIONS['branch_list'],
            choices=choices
        ).execute()

    def repo_list(self, choices):
        return inquirer.select(
            message=super().QUESTIONS['repo_list'],
            choices=choices
        ).execute()

    def template_list(self, choices):
        raise NotImplementedError
