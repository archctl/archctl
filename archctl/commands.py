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
        """Returns a list of the"""
        raise NotImplementedError


class Commands(Command):
    def __init__(self):
        self.prompt = IPPrompt()

    COMMANDS = [
        "register",
        "list",
        "delete",
        "create",
        "upgrade",
        "preview",
        "search",
        "version",
    ]

    def run(self):
        """Returns a list of the"""
        return self.prompt.command_list(self.COMMANDS)


class Register(Command):
    def __init__(self):
        self.prompt = IPPrompt()
        self.validator = Validation(True)
        self.cli = GHCli()

    def run(self):
        repo = comm.get_repo_dataclass(self.prompt.repo_text([1, 0]))

        self.cli.cw_repo = repo
        branches = [branch["name"] for branch in self.cli.list_branches()]

        repo.def_ref = self.prompt.branch_list(branches)
        kind = self.prompt.kind_list(repo)

        self.validator.confirm_command_execution(
            repo=repo.full_name, branch=repo.def_ref, kind=kind
        )

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

        repos = [
            repo.full_name
            for repo in (self.uc.project_repos() + self.uc.template_repos())
        ]
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
        print(
            "\nNow, please indicate the GH Repo that holds the Cookiecutter Template you wish to use"
        )
        t_repo = comm.get_repo_dataclass(self.prompt.repo_text([1, -1]))

        self.cli.cw_repo = t_repo
        branches = [branch["name"] for branch in self.cli.list_branches()]

        ref = self.prompt.ref_list(branches)

        templates = [t.template for t in search_templates(self.cli, ref)]
        template = self.prompt.template_list(templates) + "@" + ref

        template = comm.get_template_version_dataclass(template, t_repo)
        templates = search_templates(self.cli, template.ref)
        if templates:
            template.template.template_path = [
                temp.template_path
                for temp in templates
                if temp.template == template.template.template
            ][0]

        if template.ref is None:
            self.cli.cw_repo = template.template.template_repo
            template.ref = self.cli.get_repo_info()["default_branch"]

        self.validator.confirm_command_execution(
            project_name=repo.full_name,
            template_repo=template.template.template_repo.full_name,
            template=template.template.template,
            version=template.template.template,
        )

        archctl.create(repo, template, False)


class Render(Command):
    def __init__(self):
        self.prompt = IPPrompt()
        self.cli = GHCli()
        self.uc = JSONConfig()

    def __p_repo_manually(self):

        # Prompt the REPO
        repo = comm.get_repo_dataclass(self.prompt.repo_text([1, -1]))

        self.cli.cw_repo = repo
        branches = [branch["name"] for branch in self.cli.list_branches()]
        # Prompt the branch from the given REPO
        branch = self.prompt.branch_list(branches)
        # Add the given REPO and branch to the answer
        repo.def_ref = branch

        return repo

    # PROMPT FOR PROJECT REPOS
    def __p_repos_manually(self):

        print(
            "Please enter one or more project repositories to upgrade!\n\t\t\t\t(One by One)"
        )

        # Loop to prompt for a REPO and branch, one by one
        continue_ = True
        repos = []
        while continue_:
            repos.append(self.__p_repo_manually())
            # Prompt for continuation
            continue_ = self.prompt.confirm()

        return repos

    def p_repo_from_config(self, repos):
        # Prompt to select which repos of the config user wants to upgrade
        repo_names = [repo.full_name for repo in repos]

        selected_repo = self.prompt.repo_list(repo_names)

        if "Other" == selected_repo:
            return self.__p_repo_manually()

        repo = [r for r in repos if r.full_name == selected_repo.full_name][0]

        print("These are the default branches setup in local config:\n")
        print(f"\t- {repo.full_name} [ Default Branch: {repo.def_ref} ]")

        continue_ = self.prompt.confirm()
        if not continue_:
            repo.def_ref = self.prompt.branch_text(repo)

        return repo

    def __p_repos_from_config(self, repos):

        # Prompt to select which repos of the config user wants to upgrade
        repo_names = [repo.full_name for repo in repos]

        selected_repos = self.prompt.repo_checkbox(repo_names)

        other = "Other" in selected_repos

        # Get a list with all the info of the Project repos the user selected
        selected_repos = [repo for repo in repos if repo.full_name in selected_repos]

        # Prompt user to confirm if he wants to proceed with the stored config or modify it
        if selected_repos:
            print("These are the default branches setup in local config:\n")
            for repo in selected_repos:
                print(f"\t- {repo.full_name} [ Default Branch: {repo.def_ref} ]")

            continue_ = self.prompt.confirm()
            if not continue_:

                # When user indicates no, question which branch of the REPO the user
                # whishes to use in each REPO
                print(
                    "Please select the default branch for each of the selected projects"
                )

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

    def p_repos(self):
        """Prompt user to select the projects to update from local config
        and optionally, add more manually
        """
        uc_repos = self.uc.project_repos()

        if uc_repos:  # If there are Project repos stored in the config
            return self.__p_repos_from_config(uc_repos)

        else:  # If there are no Project repos stored in the config
            return self.__p_repos_manually()


class Upgrade(Render):
    def __init__(self):
        self.prompt = IPPrompt()
        self.validator = Validation(True)
        self.cli = GHCli()

    def run(self):

        print("Please indicate the template you wish to use to Upgrade")

        t_repo = comm.get_repo_dataclass(self.prompt.repo_text([1, -1]))

        self.cli.cw_repo = t_repo
        branches = [branch["name"] for branch in self.cli.list_branches()]

        ref = self.prompt.ref_list(branches)

        templates = [t.template for t in search_templates(self.cli, ref)]
        template = self.prompt.template_list(templates) + "@" + ref

        template = comm.get_template_version_dataclass(template, t_repo)

        repos = super().p_repos()

        self.validator.confirm_command_execution(repos=repos, template=template)

        archctl.upgrade(repos, template, False)


class Preview(Render):
    def __init__(self):
        self.prompt = IPPrompt()
        self.validator = Validation(True)
        self.cli = GHCli()
        self.uc = JSONConfig()

    def __p_repo(self):
        """Prompt user to select the projects to update from local config
        and optionally, add more manually
        """
        uc_repos = self.uc.project_repos()

        if uc_repos:  # If there are Project repos stored in the config
            return super().p_repo_from_config(uc_repos)

        else:  # If there are no Project repos stored in the config
            return super().__p_repo_manually()

    def run(self):

        print("Please indicate the template you wish to use to Upgrade")

        t_repo = comm.get_repo_dataclass(self.prompt.repo_text([1, -1]))

        self.cli.cw_repo = t_repo
        branches = [branch["name"] for branch in self.cli.list_branches()]

        ref = self.prompt.ref_list(branches)

        templates = [t.template for t in search_templates(self.cli, ref)]
        template = self.prompt.template_list(templates) + "@" + ref

        template = comm.get_template_version_dataclass(template, t_repo)

        repo = self.__p_repo()

        self.validator.confirm_command_execution(repos=repo, template=template)

        archctl.preview(repo, template, False, False)


class Search(Command):
    def __init__(self):
        self.validator = Validation(True)
        self.prompt = IPPrompt()

    def run(self):

        t_repo = comm.get_repo_dataclass(self.prompt.repo_text([1, -1]))

        depth = self.prompt.depth_text()

        tags = self.prompt.confirm("Do you wish to search for tags?")

        self.validator.confirm_command_execution(
            repo=t_repo.full_name, depth=depth, tags=tags
        )

        archctl.search(t_repo, int(depth), tags, None)
