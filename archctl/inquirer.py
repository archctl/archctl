"""Interactive questions for the main CLI commands."""

from InquirerPy import prompt

import archctl.github as gh
import archctl.validation as val
import archctl.user_config as uc

#  GLOBAL VARIABLES
repo = None
p_repos = None
t_repo = None
t_repos = None
template = None
templates = None
last_three = None

another_repo = 'Do you want to add another repo?'
def_branches = 'Do you want to continue with this configuration?'
more_repos = 'Do you wish to add more repos manually?'


def print_info(message):
    print('\n-------------------------------------------------------------')
    print(message)
    print('-------------------------------------------------------------\n')


def list_repo_branches():
    """Returns a list with the names of the branches in the given repo"""
    if repo is not None:
        branches = gh.list_branches(repo)
        if branches:
            return branches
        else:
            return []
    else:
        return []


def get_available_templates():
    """Sets the global variable paths to contain the paths of all"""

    global templates
    templates = gh.search_templates(t_repo)

    if templates:
        return templates
    else:
        return []


def get_last_three_v():
    # Get the last three commits for that template through the GitHub API
    global last_three
    path = templates[template]
    commits = gh.get_commit(t_repo, path=path)[:3]
    if commits:
        last_three = [t_version['sha'][:8] for t_version in commits]
    else:
        last_three = []
    return last_three


def get_t_repos():
    t_repos = uc.get_t_repos()
    t_repos.append('Other')
    return t_repos


def get_p_repos():
    p_repos_ = [repo['name'] for repo in p_repos]
    p_repos_.append('Other')
    return p_repos_


# QUESTIONS
def commands():
    return [
        {
            'type': 'list',
            'name': 'command',
            'message': 'What command do you wish to perform?:',
            'choices': ['register', 'list', 'delete', 'modify', 'create', 'upgrade', 'preview', 'search', 'version']
        }
    ]


def repo_question():
    return [
        {
            'type': 'input',
            'name': 'repo',
            'message': 'Name of the repository (owner/name or URL):',
            'validate': lambda res: val.validate_repo_interactive(res),
            "invalid_message": "Repository not found in Github.com"
        }
    ]


def register_repo_question():
    return [
        {
            'type': 'input',
            'name': 'repo',
            'message': 'Name of the repository (owner/name or URL):',
            'validate': lambda res: val.validate_register_repo_interactive(res),
            "invalid_message": "Repository not found in Github.com or already registered"
        }
    ]


def modify_repo_question():
    return [
        {
            'type': 'input',
            'name': 'repo',
            'message': 'Name of the repository (owner/name) to be modified:',
            'validate': lambda res: val.validate_local_repo_interactive(res),
            "invalid_message": "Repository not found in local config"
        }
    ]


def repos_checkbox_question():
    return [
        {
            'type': 'checkbox',
            'name': 'selected_repos',
            'message': 'Select the Project repos to update from local config:',
            'choices': get_p_repos(),
            'validate': val.validate_repos_checkbox,
            'invalid_message': 'Should be at least 1 selection',
            'instruction': '(Please, select at least 1 repository)',
        }
    ]


def kind_question():
    return [
        {
            'type': 'list',
            'name': 'kind',
            'message': 'Kind of repository:',
            'choices': ['Project', 'Template'],
            'validate': lambda res: val.validate_kind_interactive(repo, res),
            'invalid_message': 'No templates found in the repository'
        }
    ]


def name_question():
    return [
        {
            'type': 'input',
            'name': 'name',
            'message': 'Name of the project that will be created\n'
                    '(If no org is indicated, the repo will be created under the logged user account):',
            'validate': lambda res: val.validate_repo_name_available_interactive(res),
            "invalid_message": "Repository already exists"
        }
    ]


def t_repo_question():
    return [
        {
            'type': 'input',
            'name': 't_repo',
            'message': 'Name or URL of the Template\'s repository (owner/name or URL):',
            'validate': lambda res: val.validate_t_repo_interactive(res)
        }
    ]


def t_repo_config_question():
    return [
        {
            'type': 'list',
            'name': 't_repo',
            'message': 'Select a Template repo from your config:',
            'choices': get_t_repos()
        }
    ]


def branch_question():
    return [
        {
            'type': 'list',
            'name': 'branch',
            'message': 'Branch of the repository to checkout from:',
            'choices': list_repo_branches()
        }
    ]


def template_question():
    return [
        {
            'type': 'list',
            'name': 'template',
            'message': 'Template to render in the project:',
            'choices': get_available_templates()
        }
    ]


def template_version_question():
    return [
        {
            'type': 'input',
            'name': 't_version',
            'message': ('Version of the template to use. (Last three: ' + str(get_last_three_v()) + '):'),
            'validate': (lambda t_version: val.validate_t_version_interactive(t_repo, template, t_version))
        }
    ]


def search_depth_question():
    return [
        {
            'type': 'input',
            'name': 'depth',
            'message': 'Depth of the search for each branch\n(number of'
                    'commits/versions on each branch on each template) -1 to show all:',
            'default': '3',
            'validate': val.validate_depth_interactive
        }
    ]


def version_depth_question():
    return [
        {
            'type': 'input',
            'name': 'depth',
            'message': 'Number of renders to show info about, -1 to show all:',
            'default': '5',
            'validate': val.validate_depth_interactive
        }
    ]


def confirm_question(message):
    return [
        {
            'type': 'confirm',
            'message': message,
            'name': 'confirm',
            'default': True,
        }
    ]


# PROMPTS FOR TEMPLATE REPO
def prompt_t_repo_manually():
    global t_repo

    t_repo = prompt(t_repo_question())['t_repo']


def prompt_t_repo_from_config():
    global t_repo

    t_repo = prompt(t_repo_config_question())['t_repo']

    if t_repo == 'Other':
        prompt_t_repo_manually()


def prompt_t_repo():
    """If there are tempalte repos stored in local config, prompt those
        if there are not, prompt the user to input it manually
    """
    # Gets all the template repos in local config
    t_repos = uc.get_t_repos()

    if t_repos:  # If there are template repos in local config
        prompt_t_repo_from_config()
    else:  # If there aren't template repos in local config
        prompt_t_repo_manually()


# PROMPT FOR PROJECT REPOS
def prompt_p_repos_manually():
    global p_repos, repo

    print_info('Please enter one or more project repositories to upgrade!\n\t\t\t\t(One by One)')

    # Loop to prompt for a repo and branch, one by one
    continue_ = True
    while continue_:
        # Prompt the repo
        repo = prompt(repo_question())['repo']
        # Prompt the branch from the given repo
        branch = prompt(branch_question())['branch']
        # Add the given repo and branch to the answer
        p_repos.append({'name': '/'.join(repo), 'def_branch': branch})
        # Prompt for continuation
        continue_ = prompt(confirm_question(another_repo))['confirm']


def prompt_p_repos_from_config():
    global p_repos, repo, other

    # Prompt to select which repos of the config user wants to upgrade
    selected_p_repos = prompt(repos_checkbox_question())['selected_repos']

    if 'Other' in selected_p_repos:
        selected_p_repos.pop(selected_p_repos.index('Other'))
        other = True

    # Get a list with all the info of the Project repos the user selected
    p_repos = [repo for repo in p_repos if repo['name'] in selected_p_repos]

    # Prompt user to confirm if he wants to proceed with the stored config or modify it
    print_info('These are the def branches setup in local config:\n' + str(p_repos))
    continue_ = prompt(confirm_question(def_branches))['confirm']

    if not continue_:  # If user says yes, p_repos holds all the info as a global var

        # When user indicates no, question which branch of the repo the user
        # whishes to use in each repo
        print_info('Please select the default branch for each of the selected projects')

        for p_repo in p_repos:
            repo = p_repo['name']
            new_p_repo = {'name': p_repo['name'], 'def_branch': prompt(branch_question())['branch']}
            p_repos[p_repos.index(p_repo)] = new_p_repo

        # Now, p_repo holds all the info as a global var


def prompt_p_repos():
    """ Prompt user to select the projects to update from local config
        and optionally, add more manually
    """
    global p_repos

    # Get the Project Repos stored in the user config
    p_repos = uc.get_p_repos()

    if p_repos:  # If there are Project repos stored in the config
        prompt_p_repos_from_config()

        # If user selected other
        if other:
            prompt_p_repos_manually()
        else:  # If user didn't select other
            continue_ = prompt(confirm_question(more_repos))['confirm']
            if continue_:
                prompt_p_repos_manually()
    else:  # If there are no Project repos stored in the config
        prompt_p_repos_manually()


# REGISTER
def register_interactive():
    global repo

    answers = prompt(register_repo_question())
    repo = answers['repo']

    answers = {**answers, **prompt(kind_question())}

    if answers['kind'] == 'Template':
        return answers
    else:
        return {**answers, **prompt(branch_question())}


# DELETE
def delete_interactive():
    return prompt(modify_repo_question())


# DELETE
def modify_interactive():

    answers = prompt(modify_repo_question())

    print_info('Now, please enter the infomation to update')

    return {**answers, **register_interactive()}


# CREATE
def create_interactive():
    global template

    answers = prompt(name_question())

    prompt_t_repo()

    answers['t_repo'] = t_repo

    answers = {**answers, **prompt(template_question())}
    template = answers['template']

    return {**answers, **prompt(template_version_question())}


# UPGRADE
def upgrade_interactive():
    global t_repo, template, repo, p_repos

    answers = {}

    prompt_p_repos()
    answers['projects'] = p_repos

    prompt_t_repo()
    answers['t_repo'] = t_repo

    answers = {**answers, **prompt(template_question())}
    template = answers['template']

    answers = {**answers, **prompt(template_version_question())}
    return answers


# SEARCH
def search_interactive():

    prompt_t_repo()

    answers = {}
    answers['t_repo'] = t_repo

    return {**answers, **prompt(search_depth_question())}


# VERSION
def version_interactive():

    prompt_t_repo()

    answers = {}
    answers['t_repo'] = t_repo

    return {**answers, **prompt(version_depth_question())}


def interactive_prompt():

    command = prompt(commands())['command']

    if command == "register":
        return register_interactive()
    elif command == "list":
        # Call list
        pass
    elif command == "delete":
        return delete_interactive()
    elif command == "modify":
        return modify_interactive()
    elif command == "create":
        return create_interactive()
    elif command == "upgrade":
        return upgrade_interactive()
    elif command == "preview":
        return upgrade_interactive()
    elif command == "search":
        return search_interactive()
    elif command == "version":
        return version_interactive()
    else:
        print("Command not supported in interactive use")
