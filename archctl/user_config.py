"""Module to handle the local user config"""
import json
from abc import ABC, abstractmethod
from os import R_OK, access, environ
from os.path import isfile

import archctl.commons as comm


class UserConfig(ABC):

    @abstractmethod
    def create_config_file(self):
        """Create the user config file if it didn't exist"""

    @abstractmethod
    def project_repos(self):
        """Get all the Project repos stored in the user config"""

    @abstractmethod
    def template_repos(self):
        """Get all the Template repos stored in the user config"""

    @abstractmethod
    def set_p_repos(self, p_repos: list[comm.Repo]):
        """Set the project repos"""

    @abstractmethod
    def set_t_repos(self, t_repos: list[comm.Repo]):
        """Set the template repos"""

    @abstractmethod
    def add_p_repo(self, p_repo):
        """Add a project repo"""

    @abstractmethod
    def add_t_repo(self, t_repo):
        """Add a template repo"""

    @abstractmethod
    def delete_repo(self, repo):
        """Delete a repo from the user config"""

    @abstractmethod
    def repo_exists(self, repo):
        """Check if a repo exists"""


class JSONConfig(UserConfig):

    __CONFIG_PATH = environ['HOME'] + '/.archctl'
    __BASE_CONFIG = {'t_repos': [], 'p_repos': []}

    def __user_config_exists(self):
        """Check if the user config file exists"""
        return isfile(self.__CONFIG_PATH) and access(self.__CONFIG_PATH, R_OK)

    def __read_user_config(self):
        """Read user config file and return the dictionary"""
        if not self.__user_config_exists():
            return False
        try:
            with open(self.__CONFIG_PATH) as json_file:
                return json.load(json_file)
        except json.decoder.JSONDecodeError:
            self.create_config_file()
            return {'t_repos': [], 'p_repos': []}

    def __write_user_config(self, config):
        """Overwrite user config with new config"""
        with open(self.__CONFIG_PATH, 'w') as outfile:
            json.dump(config, outfile)

    def create_config_file(self):
        """Create the user config file if it didn't exist"""
        self.__write_user_config(self.__BASE_CONFIG)

    def project_repos(self) -> list[comm.Repo]:
        """Get all the Project repos stored in the user config"""
        config = self.__read_user_config()
        return [comm.Repo(**repo) for repo in config['p_repos']]

    def template_repos(self) -> list[comm.Repo]:
        """Get all the Template repos stored in the user config"""
        config = self.__read_user_config()
        return [comm.Repo(**repo) for repo in config['t_repos']]

    def set_p_repos(self, p_repos: list[comm.Repo]):
        """Set the project repos"""
        config = self.__read_user_config()
        config['p_repos'] = json.loads(json.dumps(p_repos, cls=comm.EnhancedJSONEncoder))
        self.__write_user_config(config)

    def set_t_repos(self, t_repos: list[comm.Repo]):
        """Set the template repos"""
        config = self.__read_user_config()
        config['t_repos'] = json.loads(json.dumps(t_repos, cls=comm.EnhancedJSONEncoder))
        self.__write_user_config(config)

    def add_p_repo(self, p_repo):
        """Add a project repo"""

        p_repo = comm.get_repo_dataclass(p_repo)
        p_repos = self.project_repos()

        if p_repos:
            match = [r for r in p_repos if r.full_name == p_repo.full_name]
        else:
            match = False
            p_repos = []

        if not match:
            p_repos.append(p_repo)
            self.set_p_repos(p_repos)
            return True

        return False

    def add_t_repo(self, t_repo):
        """Add a template repo"""

        t_repo = comm.get_repo_dataclass(t_repo)
        t_repos = self.template_repos()

        if t_repos:
            match = [r for r in t_repos if r.full_name == t_repo.full_name]
        else:
            match = False
            t_repos = []

        if not match:
            t_repos.append(t_repo)
            self.set_t_repos(t_repos)
            return True

        return False

    def delete_repo(self, repo):
        repo = comm.get_repo_dataclass(repo)

        p_repos = self.project_repos()
        t_repos = self.template_repos()

        match_p = [r for r in p_repos if r.full_name == repo.full_name]
        match_t = [r for r in t_repos if r.full_name == repo.full_name]

        if match_p:
            p_repos.remove(match_p[0])
            self.set_p_repos(p_repos)
            return True
        elif match_t:
            t_repos.remove(match_t[0])
            self.set_t_repos(t_repos)
            return True

        return False

    def repo_exists(self, repo):
        repo = comm.get_repo_dataclass(repo)

        p_repos = self.project_repos()
        t_repos = self.template_repos()

        if p_repos:
            p_repos = [r for r in p_repos if r.full_name == repo.full_name]
        else:
            p_repos = False

        if t_repos:
            t_repos = [r for r in t_repos if r.full_name == repo.full_name]
        else:
            t_repos = False

        return p_repos or t_repos
