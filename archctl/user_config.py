"""Module to handle the local user config"""
from os import access, R_OK, environ
from os.path import isfile
import json

config_path = environ['HOME'] + '/.archctl'

base_config = {'t_repos': [], 'p_repos': []}


def user_config_exists():
    """Check if the user config file exists"""

    return isfile(config_path) and access(config_path, R_OK)


def read_user_config():
    """Read user config file and return the dictionary"""

    with open(config_path) as json_file:
        return json.load(json_file)


def write_user_config(config):
    """Overwrite user config with new config"""

    with open(config_path, 'w') as outfile:
        json.dump(config, outfile)


def create_config_file():
    """Create the user config file if it didn't exist"""

    if not user_config_exists():
        with open(config_path, 'w') as outfile:
            json.dump(base_config, outfile)


def check_p_repo_format(*args):
    """Check if p_repo has the correct format (Dict with name and def_branch keys)"""

    for p_repo in args:
        if not ('name' in p_repo and 'def_branch' in p_repo and isinstance(p_repo, dict)):
            return False

    return True


def check_t_repo_format(*args):
    """Check if t_repo has the correct format (String)"""

    for t_repo in args:
        if not isinstance(t_repo, str):
            return False

    return True


def get_p_repos():
    """Get all the Project repos stored in the user config"""
    return read_user_config()['p_repos']


def get_t_repos():
    """Get all the Template repos stored in the user config"""
    return read_user_config()['t_repos']


def set_p_repos(p_repos):
    """Set the project repos"""

    config = read_user_config()
    config['p_repos'] = p_repos
    write_user_config(config)


def set_t_repos(t_repos):
    """Set the template repos"""

    config = read_user_config()
    config['t_repos'] = t_repos
    write_user_config(config)


def update_p_repo(p_repo_id, new_p_repo):
    """Update a project repo"""

    p_repos = get_p_repos()
    match = [x for x in p_repos if x['name'] == p_repo_id]

    if match and check_p_repo_format(match, new_p_repo):
        p_repos[p_repos.index(match)] = new_p_repo
        set_p_repos(p_repos)
        return True

    return False


def update_t_repo(t_repo, new_t_repo):
    """Update a template repo"""

    if check_t_repo_format(t_repo, new_t_repo):
        t_repos = get_t_repos()
        if t_repo in t_repos:
            t_repos[t_repos.index(t_repo)] = new_t_repo
            set_t_repos(t_repos)
            return True

    return False


def update_repo(old_repo, new_repo, kind):
    if kind == 'Project':
        if p_repo_name_exists(old_repo):
            return update_p_repo(old_repo, new_repo)
        else:
            return delete_t_repo(old_repo) and add_p_repo(new_repo)
    elif kind == 'Template':
        if t_repo_exists(old_repo):
            return update_t_repo(old_repo, new_repo)
        else:
            return delete_p_repo(old_repo) and add_t_repo(new_repo)


def add_p_repo(p_repo):
    """Add a project repo"""

    if check_p_repo_format(p_repo):
        p_repos = get_p_repos()
        match = [x for x in p_repos if x == p_repo]
        if not match:
            p_repos.append(p_repo)
            set_p_repos(p_repos)
            return True

    return False


def add_t_repo(t_repo):
    """Add a template repo"""

    if check_t_repo_format(t_repo):
        t_repos = get_t_repos()
        if t_repo not in t_repos:
            t_repos.append(t_repo)
            set_t_repos(t_repos)
            return True

    return False


def delete_p_repo(p_repo_id):
    """Delete a project repo"""

    p_repos = get_p_repos()
    match = [x for x in p_repos if x['name'] == p_repo_id]
    if match:
        p_repos.remove(match[0])
        set_p_repos(p_repos)
        return True

    return False


def delete_t_repo(t_repo):
    """Delete a template repo"""

    t_repos = get_t_repos()
    if t_repo in t_repos:
        t_repos.remove(t_repo)
        set_t_repos(t_repos)
        return True

    return False


def delete_repo(repo):
    return delete_p_repo(repo) or delete_t_repo(repo)


def t_repo_exists(t_repo):
    t_repos = get_t_repos()

    if t_repo in t_repos:
        return True
    else:
        return False


def p_repo_name_exists(p_repo_name):
    p_repos = [p_repo['name'] for p_repo in get_p_repos()]

    if p_repo_name in p_repos:
        return True
    else:
        return False


def p_repo_exists(p_repo):
    p_repos = get_p_repos()

    if p_repo in p_repos:
        return True
    else:
        return False
