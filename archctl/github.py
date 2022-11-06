"""Module to perform http requests to the GitHub API and handle the Auth"""
import subprocess
import requests
import re

api_github = "https://api.github.com"
cookiecutter_dir_pattern = re.compile('^(.*\/)*\{\{cookiecutter\..*\}\}$')


def set_headers():
    """Return the default headers for the API calls"""
    return {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + get_user_token()
    }


def get_request(request):
    """Makes a get request"""

    response = requests.get(request, headers=set_headers())

    if response.status_code == 200:
        return response.json()
    else:
        return None


# def org_or_user(owner):
#     """Return 0 if its an org, 1 if its a user, -1 if it doesn't exist"""

#     request = f"{api_github}/orgs/{owner}"
#     response = requests.get(request, headers=set_headers())

#     if response.status_code == 200:
#         return 0
#     else:
#         request = f"{api_github}/users/{owner}"
#         response = requests.get(request, headers=set_headers())

#         if response.status_code == 200:
#             return 1
#         else:
#             return -1


def check_user_auth():
    """Check if user is logged in via gh CLI"""

    cmd = 'gh auth status'

    try:
        subprocess.run(cmd.split(), capture_output=True, check=True)
        return True

    except subprocess.CalledProcessError:
        return False


def get_logged_user():
    """Get the logged in user name via gh CLI"""

    cmd = 'gh auth status'

    if check_user_auth():
        status = subprocess.getoutput(cmd).split()
        user = status[status.index('as') + 1]
        return user

    else:
        return None


def get_user_token():
    """Get the user token"""

    cmd = 'gh auth token'

    try:
        output = subprocess.run(cmd.split(), capture_output=True, check=True)
        return output.stdout.decode()[:-1]

    except subprocess.CalledProcessError:
        print("Couldn't get the gh token")


def get_branch(owner, repo, ref=None):
    """Get the info of one (ref is not None) or all (ref is None) the branches in a repo"""

    request = f'{api_github}/repos/{owner}/{repo}/branches'
    if ref is not None:
        request += f'/{ref}'

    return get_request(request)


def get_commit(owner, repo, depth=None, path=None):
    """Get a list of commits in a given repo path"""

    request = f'{api_github}/repos/{owner}/{repo}/commits'
    if path is not None and depth is not None:
        request += f'?path={path}&per_page={depth}'
    elif path is None and depth is not None:
        request += f'?per_page={depth}'
    elif path is not None and depth is None:
        request += f'?path={path}'

    return get_request(request)


def get_content(owner, repo, path, ref=None):
    """ Get the content of the given branch in the given repo,
        checked out at the given ref
    """

    request = api_github + f'/repos/{owner}/{repo}/contents/{path}'
    if ref is not None:
        request += f'?ref={ref}'

    return get_request(request)


def get_tree(owner, repo, tree_sha=None, recursive='0'):
    """Get a tree of the given repo, if sha is None, get the root tree of the repo"""

    if tree_sha is None:
        default_branch = get_repo_info(owner, repo)['default_branch']
        tree_sha = get_branch(owner, repo, default_branch)['commit']['commit']['tree']['sha']

    request = f'{api_github}/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=0'

    return get_request(request)


def get_repo_info(owner, repo):
    """Get the general info of a repo"""

    request = api_github + f'/repos/{owner}/{repo}'

    return get_request(request)


# def tree_contains_cookiecutter_dir(content):
#     """Given a dictionary, search for a cookiecutter directory and returns accordingly"""

#     for item in content:
#         if cookiecutter_dir_pattern.match(item['path']):
#             return True

#     return False


def search_templates(owner, repo, ref=None):
    """ Search for cookiecutter templates in the given repo@ref
        Returns a dictionary where the name of the template is the key and
        the path to the template is the value.
    """

    # Get the tree of files recursively, to get all the files in the repo
    # with the lowest amount of info
    tree = get_tree(owner, repo, ref, '1')

    if tree is None:
        return None

    # Get all the directories in the tree that match the cookiecutter project
    # template folder regular expresion --> ^(.*\/)*\{\{cookiecutter\..*\}\}$
    dirs = [dir for dir in tree['tree'] if (dir['mode'] == '040000' and cookiecutter_dir_pattern.match(dir['path']))]

    if len(dirs) == 1 and '/' not in dirs[0]['path']:
        return {repo: dirs[0]['path']}
    else:
        # From that list of dirs, split the path to get all the folder's individual
        # names and select the name of the parent to get the template name
        paths = ['/'.join(template['path'].split('/')[:-1]) for template in dirs if '/' in template['path']]
        templates = [template['path'].split('/')[-2] for template in dirs if '/' in template['path']]

    return dict(zip(templates, paths))


def create_repo(repo, description='', private='false', org=None):
    """Create a GitHub repo"""

    request = None
    if org is None:
        request = f'{api_github}/user/repos'
    else:
        request = f'{api_github}/orgs/{org}/repos'

    body = {
        'name': repo,
        'description': description,
        'private': private,
        'auto_init': 'true'
    }

    response = requests.post(request, headers=set_headers(), json=body)

    if response.status_code == 201:
        return response.json()
    else:
        return None


def create_pr(owner, repo, head, base, title='PR created by Archctl'):
    """Create a pull request in the given repo"""

    request = f'{api_github}/repos/{owner}/{repo}/pulls'

    body = {
        'title': title,
        'head': head,
        'base': base,
        'auto_init': 'true'
    }

    response = requests.post(request, headers=set_headers(), json=body)

    if response.status_code == 201:
        return response.json()
    else:
        return None


def repo_exists(owner, repo):
    if get_repo_info(owner, repo) is not None:
        return True
    else:
        return False
