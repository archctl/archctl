import logging
import subprocess
from abc import ABC, abstractmethod

import json

import archctl.commons as comm

logger = logging.getLogger(__name__)

# api_github = "https://api.github.comm"


class GithubIface(ABC):
    """Interface for the github controller"""

    @abstractmethod
    def get_repo_info(self):
        """Get the general info of a repo"""
        raise NotImplementedError

    @abstractmethod
    def get_default_branch(self):
        """Return the default branch of the given repo"""
        raise NotImplementedError

    @abstractmethod
    def get_branch_info(self, branch):
        """Comment"""
        raise NotImplementedError

    @abstractmethod
    def list_branches(self):
        """Returns a list of the"""
        raise NotImplementedError

    @abstractmethod
    def branch_exists(self, branch):
        """Comment"""
        raise NotImplementedError

    @abstractmethod
    def get_commits(self, path=None):
        """Comment"""
        raise NotImplementedError

    @abstractmethod
    def list_tags(self):
        """Comment"""
        raise NotImplementedError

    @abstractmethod
    def get_tree(self, tree_sha=None, recursive="0"):
        """Get a tree of the given repo, if sha is None, get the root tree of the repo"""
        raise NotImplementedError

    @abstractmethod
    def create_repo(self, description="", private=False):
        """Comment"""
        raise NotImplementedError

    @abstractmethod
    def create_dir(
        self, path, commit_message="Commit via Archctl", content="", branch=None
    ):
        """Create directory in repo"""
        raise NotImplementedError

    @abstractmethod
    def delete_repo(self, confirm=True):
        """Comment"""
        raise NotImplementedError

    @abstractmethod
    def create_pr(self, head, base, title="PR created by Archctl"):
        """Comment
        Title
        Body
        Base branch where to merge
        Head branch what to merge
        """
        raise NotImplementedError


class GHCli(GithubIface):
    def __init__(self):
        comm.auth_status()
        self._cw_repo: comm.Repo = comm.Repo(None, None, None, None, None, None)

    @property
    def cw_repo(self) -> comm.Repo:
        return self._cw_repo

    @cw_repo.setter
    def cw_repo(self, input_repo):
        if isinstance(input_repo, str):
            self._cw_repo: comm.Repo = comm.get_repo_dataclass(input_repo)
        elif isinstance(input_repo, comm.Repo):
            self._cw_repo: comm.Repo = input_repo
        else:
            logger.debug(
                "Formato de repo no reconocido al establecer el cw_repo de GHCli"
            )

    def __get_request(self, request):
        """Makes a get request via gh cli"""

        cmd = f"gh api {request}"

        try:
            logger.debug(f"Making request {request} to GH API via GH CLI")
            response = subprocess.getoutput(cmd)
            return json.loads(response)

        except subprocess.CalledProcessError:
            logger.debug("Problem running the GitHub CLI command")
            return {}

        except ValueError:
            logger.debug("Problem decoding GitHub API response")
            return {}

    def get_repo_info(self):
        """Get the general info of a repo"""

        request = f"repos/{self.cw_repo.full_name}"

        return self.__get_request(request)

    def get_default_branch(self):
        """Return the default branch of the given repo"""
        return self.get_repo_info()["default_branch"]

    def get_branch_info(self, branch):
        """Comment"""

        request = f"repos/{self.cw_repo.full_name}/branches/{branch}"

        return self.__get_request(request)

    def list_branches(self):
        """Returns a list of the"""

        request = f"repos/{self.cw_repo.full_name}/branches"

        return self.__get_request(request)

    def branch_exists(self, branch):
        """Comment"""

        branches = [branch["name"] for branch in self.list_branches()]

        return branch in branches

    def get_commits(self, path=None, sha=None):
        """Comment"""

        request = f"repos/{self.cw_repo.full_name}/commits"

        if path is not None and sha is None:
            request += f"?path={path}"
        elif path is None and sha is not None:
            request += f"?sha={sha}"
        elif path is not None and sha is not None:
            request += f"?sha={sha}&path={path}"

        return self.__get_request(request)

    def list_tags(self):
        """Lists all tags in the repo"""

        request = f"repos/{self.cw_repo.full_name}/tags"

        return self.__get_request(request)

    def get_tree(self, ref=None, recursive="0"):
        """Get a tree of the given repo, if sha is None, get the root tree of the repo"""

        if ref is None:
            ref = self.get_default_branch()

        request = f"repos/{self.cw_repo.full_name}/git/trees/{ref}?recursive=0"

        return self.__get_request(request)

    def create_repo(self, description="", private=True):
        """Comment"""

        cmd = f"gh repo create {self.cw_repo.full_name} --add-readme -d '{description}'"

        if private:
            cmd += " --private"
        else:
            cmd += " --public"

        try:
            if not subprocess.getoutput(cmd).startswith("https://"):
                raise subprocess.CalledProcessError(1, cmd)

            return True

        except subprocess.CalledProcessError:
            logger.debug("Could not create the repo")
            return False

    def create_dir(
        self, path, commit_message="Commit via Archctl", content="", branch=None
    ):
        """Create directory in repo"""

        request = f"repos/{self.cw_repo.full_name}/contents/{path}"

        body = {"message": commit_message, "content": content}

        if branch is not None:
            body["branch"] = branch

        cmd1 = ["echo", "-n", json.dumps(body)]

        cmd2 = ["gh", "api", "-X", "PUT", request, "--input", "-"]

        try:
            # logger.info(f'Making request \'{cmd}\' to GH API via GH CLI')

            ps = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
            output = subprocess.check_output(cmd2, stdin=ps.stdout)
            ps.wait()

            print(output)

        except subprocess.CalledProcessError:
            logger.debug("Problem running the GitHub CLI command")
            return False

        except ValueError:
            logger.debug("Problem decoding GitHub API response")
            return False

    def delete_repo(self, confirm=True):
        """Comment"""

        cmd = f"gh repo delete {self.cw_repo.full_name}"

        if confirm:
            cmd += " --confirm"

        try:
            if subprocess.getoutput(cmd) != "":
                raise subprocess.CalledProcessError(1, cmd)

        except subprocess.CalledProcessError:
            logger.debug("Could not delete the repo")
            return False

    def create_pr(self, head, base, title="PR created by Archctl"):
        """Comment
        Title
        Body
        Base branch where to merge
        Head branch what to merge
        """

        cmd = f'gh pr create -R {self.cw_repo.full_name} -B {base} -H {head} -t "{title}" -b ""'

        try:
            print(subprocess.getoutput(cmd))

        except subprocess.CalledProcessError:
            logger.debug("Could not delete the repo")
            return False
