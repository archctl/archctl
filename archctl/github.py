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


def parse_repo_name(repo):
    """Parse user input (repo | owner/repo | URL) to a list of [owner, repo]"""

    s_repo = repo.split('/')  # Split the user input with sep '/'

    # User input is a URL
    if repo.startswith('https://github.com/'):
        if repo.endswith('/'):
            s_repo.pop()

        return s_repo[-2:]
    else:
        if len(s_repo) == 1:  # User input is repo
            return [get_logged_user(), repo]
        elif len(s_repo) == 2:  # User input is owner/repo
            return s_repo
        else:  # More than 1 '/' means user error
            return None  # Action if repo is not correctly entered


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


def get_branch(repo, ref=None):
    """Get the info of one (ref is not None) or all (ref is None) the branches in a repo"""

    repo = parse_repo_name(repo)

    request = f'{api_github}/repos/{repo[0]}/{repo[1]}/branches'
    if ref is not None:
        request += f'/{ref}'

    return get_request(request)


def get_default_branch(repo):
    """Return the default branch of the given repo"""
    return get_repo_info(repo)['default_branch']


def list_branches(repo):
    """Return the list of branches in the repo"""
    return [branch['name'] for branch in get_branch(repo)]


def branch_exists(repo, ref):
    """Return true if the branch exists in the given repo"""
    # Get all branches
    branches = list_branches(repo)
    # Check if the given branch exists
    return ref in branches


def get_commit(repo, depth=None, path=None):
    """Get a list of commits in a given repo path"""

    repo = parse_repo_name(repo)

    request = f'{api_github}/repos/{repo[0]}/{repo[1]}/commits'
    if path is not None and depth is not None:
        request += f'?path={path}&per_page={depth}'
    elif path is None and depth is not None:
        request += f'?per_page={depth}'
    elif path is not None and depth is None:
        request += f'?path={path}'

    return get_request(request)


def get_content(repo, path, ref=None):
    """ Get the content of the given branch in the given repo,
        checked out at the given ref
    """

    repo = parse_repo_name(repo)

    request = api_github + f'/repos/{repo[0]}/{repo[1]}/contents/{path}'
    if ref is not None:
        request += f'?ref={ref}'

    return get_request(request)


def get_tree(repo, tree_sha=None, recursive='0'):
    """Get a tree of the given repo, if sha is None, get the root tree of the repo"""

    if tree_sha is None:
        default_branch = get_default_branch(repo)
        tree_sha = get_branch(repo, default_branch)['commit']['commit']['tree']['sha']

    repo = parse_repo_name(repo)

    request = f'{api_github}/repos/{repo[0]}/{repo[1]}/git/trees/{tree_sha}?recursive=0'

    return get_request(request)


def get_repo_info(repo):
    """Get the general info of a repo"""

    repo = parse_repo_name(repo)

    request = api_github + f'/repos/{repo[0]}/{repo[1]}'

    return get_request(request)


def create_repo(repo, description='', private='false'):
    """Create a GitHub repo"""

    repo = parse_repo_name(repo)

    request = None
    if repo[0] == get_logged_user():
        request = f'{api_github}/user/repos'
    else:
        request = f'{api_github}/orgs/{repo[0]}/repos'

    body = {
        'name': repo[1],
        'description': description,
        'private': private,
        'auto_init': 'true'
    }

    response = requests.post(request, headers=set_headers(), json=body)

    if response.status_code == 201:
        return response.json()
    else:
        return None


def delete_repo(repo):
    """Delete a GitHub repo"""

    repo = parse_repo_name(repo)

    request = f'{api_github}/repos/{repo[0]}/{repo[1]}'

    response = requests.delete(request, headers=set_headers())

    if response.status_code == 204:
        return response.json()
    else:
        return vars(response)


def create_dir(repo, path):
    """Create directory in repo"""

    repo = parse_repo_name(repo)

    request = f'{api_github}/repos/{repo[0]}/{repo[1]}/contents/{path}'

    body = {
        'message': 'Test',
        'content': ''
    }

    response = requests.put(request, headers=set_headers(), json=body)

    if response.status_code in [201, 200]:
        return response.json()
    else:
        return None


def create_pr(repo, head, base, title='PR created by Archctl'):
    """Create a pull request in the given repo"""

    repo = parse_repo_name(repo)

    request = f'{api_github}/repos/{repo[0]}/{repo[1]}/pulls'

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


def has_templates(repo, ref=None):
    """Returns true if the repo has cookiecutter templates at the given ref"""

    # Get the tree of files recursively, to get all the files in the repo
    # with the lowest amount of info
    tree = get_tree(repo, ref, '1')

    if tree is None:
        return False

    for dir in tree['tree']:
        if dir['mode'] == '040000' and cookiecutter_dir_pattern.match(dir['path']):
            return True

    return False


def search_templates(repo, ref=None):
    """ Search for cookiecutter templates in the given repo@ref
        Returns a dictionary where the name of the template is the key and
        the path to the template is the value.
    """

    # Get the tree of files recursively, to get all the files in the repo
    # with the lowest amount of info
    tree = get_tree(repo, ref, '1')

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


def repo_exists(repo):
    if get_repo_info(repo) is not None:
        return True
    else:
        return False
