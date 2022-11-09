"""Interactive questions for the main CLI commands."""

import logging

from InquirerPy import prompt

import archctl.github as gh
import archctl.validation as val
import archctl.user_config as uc
import archctl.main as arch

logger = logging.getLogger(__name__)

#  GLOBAL VARIABLES
REPO = None
PROJECT_REPOS = None
TEMPLATE_REPO = None
TEMPLATE_REPOS = None
TEMPLATE = None
TEMPLATES = None

ANOTHER_REPO = 'Do you want to add another REPO?'
DEF_BRANCHES = 'Do you want to continue with this configuration?'
MORE_REPOS = 'Do you wish to add more repos manually?'


def print_info(message):
    print('\n-------------------------------------------------------------')
    print(message)
    print('-------------------------------------------------------------\n')


def list_repo_branches():
    """Returns a list with the names of the branches in the given REPO"""
    if REPO is not None:
        branches = gh.list_branches(REPO)
        if branches:
            return branches
        else:
            return []
    else:
        return []


def get_available_templates():
    """Sets the global variable paths to contain the paths of all"""

    global TEMPLATES
    TEMPLATES = gh.search_templates(TEMPLATE_REPO)

    if TEMPLATES:
        return TEMPLATES
    else:
        return []


def get_last_three_v():
    # Get the last three commits for that TEMPLATE through the GitHub API
    path = TEMPLATES[TEMPLATE]
    commits = gh.get_commit(TEMPLATE_REPO, path=path)[:3]
    if commits:
        last_three = [t_version['sha'][:8] for t_version in commits]
    else:
        last_three = []
    return last_three


def get_t_repos():
    return TEMPLATE_REPOS.append('Other')


def get_p_repos():
    p_repos = [repo['name'] for repo in PROJECT_REPOS]
    p_repos.append('Other')
    return p_repos


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
            'name': 'old_repo',
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
            'validate': lambda res: val.validate_kind_interactive(REPO, res),
            'invalid_message': 'No TEMPLATES found in the repository'
        }
    ]


def name_question():
    return [
        {
            'type': 'input',
            'name': 'name',
            'message': 'Name of the project that will be created\n'
                    '(If no org is indicated, the REPO will be created under the logged user account):',
            'validate': lambda res: val.validate_repo_name_available_interactive(res),
            "invalid_message": "Repository already exists"
        }
    ]


def t_repo_question():
    return [
        {
            'type': 'input',
            'name': 'template_repo',
            'message': 'Name or URL of the Template\'s repository (owner/name or URL):',
            'validate': lambda res: val.validate_t_repo_interactive(res)
        }
    ]


def t_repo_config_question():
    return [
        {
            'type': 'list',
            'name': 'template_repo',
            'message': 'Select a Template REPO from your config:',
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
            'name': 'template_version',
            'message': ('Version of the TEMPLATE to use. (Last three: ' + str(get_last_three_v()) + '):'),
            'validate': (lambda t_version: val.validate_t_version_interactive(TEMPLATE_REPO, TEMPLATE, t_version))
        }
    ]


def search_depth_question():
    return [
        {
            'type': 'input',
            'name': 'depth',
            'message': 'Depth of the search for each branch\n(number of'
                    'commits/versions on each branch on each TEMPLATE) -1 to show all:',
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
    global TEMPLATE_REPO

    TEMPLATE_REPO = prompt(t_repo_question())['template_repo']


def prompt_t_repo_from_config():
    global TEMPLATE_REPO

    TEMPLATE_REPO = prompt(t_repo_config_question())['template_repo']

    if TEMPLATE_REPO == 'Other':
        prompt_t_repo_manually()


def prompt_t_repo():
    """If there are tempalte repos stored in local config, prompt those
        if there are not, prompt the user to input it manually
    """
    # Gets all the TEMPLATE repos in local config
    t_repos = uc.get_t_repos()

    if t_repos:  # If there are TEMPLATE repos in local config
        prompt_t_repo_from_config()
    else:  # If there aren't TEMPLATE repos in local config
        prompt_t_repo_manually()


# PROMPT FOR PROJECT REPOS
def prompt_p_repos_manually():
    global PROJECT_REPOS, REPO

    print_info('Please enter one or more project repositories to upgrade!\n\t\t\t\t(One by One)')

    # Loop to prompt for a REPO and branch, one by one
    continue_ = True
    while continue_:
        # Prompt the REPO
        REPO = prompt(repo_question())['repo']
        # Prompt the branch from the given REPO
        branch = prompt(branch_question())['branch']
        # Add the given REPO and branch to the answer
        PROJECT_REPOS.append({'name': '/'.join(REPO), 'def_branch': branch})
        # Prompt for continuation
        continue_ = prompt(confirm_question(ANOTHER_REPO))['confirm']


def prompt_p_repos_from_config():
    global PROJECT_REPOS, REPO, OTHER

    # Prompt to select which repos of the config user wants to upgrade
    selected_p_repos = prompt(repos_checkbox_question())['selected_repos']

    if 'Other' in selected_p_repos:
        selected_p_repos.pop(selected_p_repos.index('Other'))
        OTHER = True

    # Get a list with all the info of the Project repos the user selected
    PROJECT_REPOS = [REPO for REPO in PROJECT_REPOS if REPO['name'] in selected_p_repos]

    # Prompt user to confirm if he wants to proceed with the stored config or modify it
    print_info('These are the def branches setup in local config:\n' + str(PROJECT_REPOS))
    continue_ = prompt(confirm_question(DEF_BRANCHES))['confirm']

    if not continue_:  # If user says yes, PROJECT_REPOS holds all the info as a global var

        # When user indicates no, question which branch of the REPO the user
        # whishes to use in each REPO
        print_info('Please select the default branch for each of the selected projects')

        for p_repo in PROJECT_REPOS:
            REPO = p_repo['name']
            new_p_repo = {'name': p_repo['name'], 'def_branch': prompt(branch_question())['branch']}
            PROJECT_REPOS[PROJECT_REPOS.index(p_repo)] = new_p_repo

        # Now, p_repo holds all the info as a global var


def prompt_p_repos():
    """ Prompt user to select the projects to update from local config
        and optionally, add more manually
    """
    global PROJECT_REPOS

    # Get the Project Repos stored in the user config
    PROJECT_REPOS = uc.get_p_repos()

    if PROJECT_REPOS:  # If there are Project repos stored in the config
        prompt_p_repos_from_config()

        # If user selected other
        if OTHER:
            prompt_p_repos_manually()
        else:  # If user didn't select other
            continue_ = prompt(confirm_question(MORE_REPOS))['confirm']
            if continue_:
                prompt_p_repos_manually()
    else:  # If there are no Project repos stored in the config
        prompt_p_repos_manually()


# REGISTER
def register_interactive():
    global REPO

    answers = prompt(register_repo_question())
    REPO = answers['repo']

    answers = {**answers, **prompt(kind_question())}

    if answers['kind'] == 'Template':
        return {**answers, **{'branch': None}}
    else:
        return {**answers, **prompt(branch_question())}


# DELETE
def delete_interactive():
    answers = {}
    answers['repo_to_delete'] = prompt(modify_repo_question())['old_repo']
    return answers


# DELETE
def modify_interactive():

    answers = prompt(modify_repo_question())

    print_info('Now, please enter the infomation to update')

    return {**answers, **register_interactive()}


# CREATE
def create_interactive():
    global TEMPLATE

    answers = prompt(name_question())

    prompt_t_repo()

    answers['template_repo'] = TEMPLATE_REPO

    answers = {**answers, **prompt(template_question())}
    TEMPLATE = answers['template']

    return {**answers, **prompt(template_version_question())}


# UPGRADE
def upgrade_interactive():
    global TEMPLATE

    answers = {}

    prompt_p_repos()
    answers['projects'] = PROJECT_REPOS

    prompt_t_repo()
    answers['template_repo'] = TEMPLATE_REPO

    answers = {**answers, **prompt(template_question())}
    TEMPLATE = answers['template']

    answers = {**answers, **prompt(template_version_question())}
    return answers


# SEARCH
def search_interactive():

    answers = {}

    prompt_t_repo()
    answers['template_repo'] = TEMPLATE_REPO

    return {**answers, **prompt(search_depth_question())}


# VERSION
def version_interactive():

    answers = {}

    prompt_t_repo()
    answers['template_repo'] = TEMPLATE_REPO

    return {**answers, **prompt(version_depth_question())}


def interactive_prompt():

    command = prompt(commands())['command']

    if command == "register":
        answers = register_interactive()
        val.confirm_command_execution_interactive(answers)
        arch.register(answers['repo'], answers['kind'], answers['branch'])

    elif command == "list":
        arch.list()

    elif command == "delete":
        answers = delete_interactive()
        val.confirm_command_execution_interactive(answers)
        arch.delete(answers['old_repo'])

    elif command == "modify":
        answers = modify_interactive()
        val.confirm_command_execution_interactive(answers)
        arch.modify(answers['old_repo'], answers['repo'], answers['kind'], answers['branch'])

    elif command == "create":
        answers = create_interactive()
        val.confirm_command_execution_interactive(answers)
        arch.create(answers['name'], answers['template_repo'], answers['template'],
                    TEMPLATES[TEMPLATE], False, answers['cookies'])

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
