from InquirerPy import inquirer
from archctl.validation import Validation
from abc import ABC, abstractmethod
import archctl.commons as comm
from InquirerPy.base.control import Choice

QUESTIONS = {
    "command_list": "Select the command you wish to perform",
    "repo_text": "Name of the repository (owner/name or URL)",
    "repo_list": "Select a repository from the list",
    "repo_checkbox": "Check the repos you want to select",
    "kind_list": "Select the kind of repository from the list",
    "branch_text": "Name of the branch",
    "branch_list": "Select the repo's branch",
    "template_list": "Select the name of template",
    "template_version_text": "Version of the template to use",
    "ref_list": "Please select a ref from the list",
    "confirm": "Do you wish to proceed",
    "depth": "Please enter the depth of the search",
}


class ArchctlPrompt(ABC):
    @abstractmethod
    def repo_text(self):
        raise NotImplementedError

    @abstractmethod
    def repo_list(self, choices):
        raise NotImplementedError

    @abstractmethod
    def repo_checkbox(self, choices):
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

    @abstractmethod
    def ref_list(self, choices):
        raise NotImplementedError

    @abstractmethod
    def depth_text(self):
        raise NotImplementedError


class IPPrompt(ArchctlPrompt):
    def __init__(self):
        self.validator = Validation(True)

    def __val_reg_repo(self, input, checks: tuple[bool, bool]):
        input = comm.get_repo_dataclass(input)
        if -1 not in checks:
            gh = bool(checks[0])
            uc = bool(checks[1])
            return self.validator.repo_exists_gh(
                input, gh
            ) and self.validator.repo_exists_uc(input, uc)
        elif checks[0] != -1:
            return self.validator.repo_exists_gh(input, bool(checks[0]))
        elif checks[1] != -1:
            return self.validator.repo_exists_uc(input, bool(checks[1]))
        else:
            return True

    def command_list(self, choices):
        return inquirer.select(
            message=QUESTIONS["command_list"], choices=choices
        ).execute()

    def repo_text(self, checks):
        return inquirer.text(
            message=QUESTIONS["repo_text"],
            validate=lambda repo: self.__val_reg_repo(repo, checks),
            invalid_message="Problem found with the given repo",
        ).execute()

    def kind_list(self, repo):
        return inquirer.select(
            message=QUESTIONS["kind_list"],
            choices=["Template", "Project"],
            validate=lambda kind: self.validator.kind(repo, kind),
            invalid_message="Given repo doesn't contain any Cookiecutter Templates",
        ).execute()

    def branch_text(self, repo):
        return inquirer.text(
            message=QUESTIONS["repo_text"],
            validate=lambda branch: self.validator.branch_exists_in_repo(repo, branch),
            invalid_message="Branch not found in the given repo",
        ).execute()

    def branch_list(self, choices):
        return inquirer.select(
            message=QUESTIONS["branch_list"], choices=choices
        ).execute()

    def repo_list(self, choices):
        return inquirer.select(
            message=QUESTIONS["repo_list"], choices=choices + [Choice(value="Other")]
        ).execute()

    def repo_checkbox(self, choices):
        return inquirer.checkbox(
            message=QUESTIONS["repo_list"],
            choices=choices + [Choice(value="Other")],
            validate=lambda res: len(res) > 0,
        ).execute()

    def template_list(self, choices):
        return inquirer.select(
            message=QUESTIONS["template_list"], choices=choices
        ).execute()

    def ref_list(self, choices):
        return inquirer.select(message=QUESTIONS["ref_list"], choices=choices).execute()

    def depth_text(self):
        return inquirer.number(
            message=QUESTIONS["depth"],
            default=3,
            min_allowed=1,
            max_allowed=10,
            invalid_message="Depth must be in range 1..10",
        ).execute()

    def confirm(self, mssg=QUESTIONS["confirm"]):
        return inquirer.confirm(message=mssg, default=True).execute()
