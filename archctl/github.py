"""Module to perform http requests to the GitHub API and handle the Auth"""
import subprocess
import requests

api_github = "https://api.github.com"


def set_headers():
    """Return the default headers for the API calls"""
    return {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + get_user_token()
    }


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
        print("User not logged in")
        return False


def get_user_token():
    """Get the user token"""

    cmd = 'gh auth token'

    try:
        output = subprocess.run(cmd.split(), capture_output=True, check=True)
        return output.stdout.decode()[:-1]

    except subprocess.CalledProcessError:
        print("Couldn't get the gh token")


def get_repo_branches(owner, repo):
    """Get the names of all the branches inside a repo"""

    request = f"{api_github}/repos/{owner}/{repo}/branches"
    branches = []

    # send get request
    response = requests.get(request, headers=set_headers()).json()

    for branch in response:
        branches.append(branch['name'])

    return branches


def get_repo_commits(owner, repo, depth=None, path=None):
    """Get a list of commits in a given repo path"""

    request = f"{api_github}/repos/{owner}/{repo}/commits"
    if path is not None and depth is not None:
        request += f'?path={path}&per_page={depth}'
    elif path is None and depth is not None:
        request += f"?per_page={depth}"
    elif path is not None and depth is None:
        request += f"?path={path}"

    # send get request
    response = requests.get(request, headers=set_headers()).json()

    commits = []
    for commit in response:
        commits.append(commit['commit']['message'])

    return commits


def get_branch_contents(owner, repo, path, ref=None):
    """ Get the content of the given branch in the given repo,
        checked out at the given ref
    """

    request = ''
    if ref is None:
        request = api_github + f"/repos/{owner}/{repo}/contents/{path}"
    else:
        request = f"{api_github}/repos/{owner}/{repo}/contents/{path}?ref={ref}"

    response = requests.get(request, headers=set_headers()).json()

    files = []
    for file in response:
        files.append(file['name'])
        # files.append({'type': file['type'], 'name': file['name']})

    return files


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
        print(response.json())
        print('Couldnt create the repo')


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
        print(response.json())
        print('Couldnt create the PR')
