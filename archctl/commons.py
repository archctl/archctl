import logging
from dataclasses import dataclass, is_dataclass, asdict
import subprocess

from json import JSONEncoder

logger = logging.getLogger(__name__)


class EnhancedJSONEncoder(JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


@dataclass
class Repo:
    owner: str
    repo: str
    full_name: str
    ssh_url: str
    https_url: str
    def_ref: str


@dataclass
class Template:
    template: str
    template_repo: Repo
    template_path: str

@dataclass
class TemplateVersion:
    template = Template
    ref: str


def get_repo_dataclass(input_repo: str) -> Repo:
    """
    Parse user input to a Repo dataclass object

    Considered input formats:
        https://github.com/{owner}/{repo}[@ref]
        git@github.com:{owner}/{repo}.git[@ref]
        {owner}/{repo}[@ref]
        {repo}[@ref]
    """
    if isinstance(input_repo, Repo):
        return input_repo

    s_repo = []
    def_ref = None

    if input_repo.startswith('git@github.com:'):
        s_repo = input_repo.split('@')

        if len(s_repo) == 3:
            def_ref = s_repo[2]
        elif len(s_repo) > 3:
            logger.error('The indicated repo contains errors in its format')

        s_repo = s_repo[1].split('.com:', 1)[1].split('.git', 1)[0].split('/')

    else:
        s_repo = input_repo.split('@')

        if len(s_repo) == 2:
            def_ref = s_repo[1]
        elif len(s_repo) > 2:
            logger.error('The indicated repo contains errors in its format')

        s_repo = s_repo[0].split('/')  # Split the user input with sep '/'

        if input_repo.startswith('https://github.com/'):  # User input is a URL
            if input_repo.endswith('/'):
                s_repo.pop()

            s_repo = s_repo[-2:]

        elif len(s_repo) == 1:  # User input is repo
            s_repo = [get_logged_user(), s_repo[0]]

        elif len(s_repo) > 2:  # More than 1 '/' means user error
            logger.error('The indicated repo contains errors in its format')

    owner = s_repo[0]
    repo = s_repo[1]
    full_name = '/'.join(s_repo)
    ssh_url = f'git@github.com:{full_name}.git'
    https_url = f'https://github.com/{full_name}'

    return Repo(owner, repo, full_name, ssh_url, https_url, def_ref)


def get_template_version_dataclass(input_template: str, input_template_repo: str) -> Template:
    """
    Parse user input to a Template dataclass object

    Considered input format:
        {template}[@ref]
        {template}[@version]
    """

    s_template = input_template.split('@')
    ref = None

    if len(s_template) == 1:
        ref = None
    elif len(s_template) == 2:
        ref = get_template_version_dataclass(s_template[1])
    else:
        logger.error('The indicated template contains errors in its format')

    template = s_template[0]
    template_repo = get_repo_dataclass(input_template_repo)

    template = Template(template, template_repo, None)


    return 


def auth_status():
    """Check if user is logged in via gh CLI"""

    cmd = 'gh auth status'

    try:
        subprocess.run(cmd.split(), capture_output=True, check=True)
        logger.debug('User is logged in')
        return True

    except subprocess.CalledProcessError:
        logger.error('User is not logged in GitHub CLI, please log in before using archctl')
        exit(1)


def __get_user_token():
    """Get the user token"""

    cmd = 'gh auth token'

    try:
        output = subprocess.run(cmd.split(), capture_output=True, check=True)
        return output.stdout.decode()[:-1]

    except subprocess.CalledProcessError:
        print("Couldn't get the gh token")


def get_logged_user():
    """Get the logged in user name via gh CLI"""

    cmd = 'gh auth status'

    if auth_status():
        status = subprocess.getoutput(cmd).split()
        user = status[status.index('as') + 1]
        return user

    else:
        return False
