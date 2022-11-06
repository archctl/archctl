"""Interactive questions for the main CLI commands."""

from InquirerPy import prompt

import archctl.github as gh
import archctl.validation as val
import archctl.user_config as uc

#  GLOBAL VARIABLES
repo = None
t_repo = None
template = None
templates = None
last_three = None


def list_repo_branches():
    """Returns a list with the names of the branches in the given repo"""
    if repo is not None:
        branches = (branch['name'] for branch in gh.get_branch(repo[0], repo[1]))
        if branches is not None:
            return branches
        else:
            return []
    else:
        return []


def get_available_templates():
    """Sets the global variable paths to contain the paths of all"""

    global templates
    templates = gh.search_templates(t_repo[0], t_repo[1])

    return templates


def get_last_three_v():
    # Get the last three commits for that template through the GitHub API
    global last_three
    path = [path for path in paths if template == path.split('/')[-2]][0]
    commits = gh.get_commit(repo[0], repo[1], path=path)[:3]
    last_three = [t_version['commit']['message'] for t_version in commits]
    return last_three


# FILTERS
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
            return [gh.get_logged_user(), repo]
        elif len(s_repo) == 2:  # User input is owner/repo
            return s_repo
        else:  # More than 1 '/' means user error
            return ''  # Action if repo is not correctly entered


# QUESTIONS
def commands():
    return [
        {
            'type': 'list',
            'name': 'command',
            'message': 'What command do you wish to perform?:',
            'choices': ['register', 'create', 'upgrade', 'preview', 'search', 'version']
        }
    ]


def repo_question():
    return [
        {
            'type': 'input',
            'name': 'repo',
            'message': 'Name of the repository (owner/name or URL):',
            'filter': parse_repo_name,
            'validate': lambda res: val.validate_repo_interactive(parse_repo_name(res)),
            "invalid_message": "Repository not found in Github.com"
        }
    ]


def repo_checkbox_question():
    return [
        {
            "type": "checkbox",
            "message": "Pick your favourites:",
            "choices": uc.get_p_repos,
            "validate": lambda result: len(result) >= 1,
            "invalid_message": "Should be at least 1 selection",
            "instruction": "(Please, select at least 1 repository)",
        }
    ]


def kind_question():
    return [
        {
            'type': 'list',
            'name': 'kind',
            'message': 'Kind of repository:',
            'choices': ['Project', 'Template']
        }
    ]


def name_question():
    return [
        {
            'type': 'input',
            'name': 'name',
            'message': ('Name of the project that will be created\n' +
                        '(If no org is indicated, the repo will be created under the logged user account):'),
            'filter': parse_repo_name,
            'validate': lambda res: val.validate_repo_name_available_interactive(parse_repo_name(res)),
            "invalid_message": "Repository already exists"
        }
    ]


def t_repo_question():
    return [
        {
            'type': 'input',
            'name': 't_repo',
            'message': 'Name or URL of the Template\'s repository (owner/name or URL):',
            'filter': parse_repo_name,
            'validate': lambda res: val.validate_t_repo_interactive(parse_repo_name(res))
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
            'message': ('Version of the template to use. (Last three: ' + str(get_last_three_v(t_repo)) + '):'),
            'validate': (lambda t_version: val.validate_t_version_interactive(t_repo, template, t_version))
        }
    ]


def search_depth_question():
    return [
        {
            'type': 'input',
            'name': 'depth',
            'message': ('Depth of the search for each branch\n(number of' +
                        'commits/versions on each branch on each template) -1 to show all:'),
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


def confirm_question():
    return [
        {
            'type': 'confirm',
            'message': 'Do you want to add another repo to upgrade?',
            'name': 'confirm',
            'default': True,
        }
    ]


# REGISTER
def register_interactive():
    global repo

    answers = prompt(repo_question() + kind_question())
    repo = answers['repo']

    return {**answers, **prompt(branch_question())}


# CREATE
def create_interactive():
    global t_repo, template

    answers = prompt(name_question() + t_repo_question())
    t_repo = answers['t_repo']

    answers = {**answers, **prompt(template_question())}
    template = answers['template']

    return {**answers, **prompt(template_version_question())}


# UPGRADE
def upgrade_interactive():
    global t_repo, template, repo

    # print('\n-------------------------------------------------------------')
    # print('Please enter one or more project repositories to upgrade!')
    # print('-------------------------------------------------------------\n')

    confirm = True
    projects = []

    while confirm:

        project = prompt(repo_question())
        repo = project['repo']

        projects.append({**project, **prompt(branch_question())})

        confirm = prompt(confirm_question())['confirm']

    answers['projects'] = projects

    answers = prompt(t_repo_question())
    t_repo = answers['t_repo']

    answers = {**answers, **prompt(template_question())}
    template = answers['template']

    answers = {**answers, **prompt(template_version_question())}
    return answers


# PREVIEW
def preview_interactive():
    global t_repo, template, repo

    answers = prompt(t_repo_question())
    t_repo = answers['t_repo']

    answers = {**answers, **prompt(template_question())}
    template = answers['template']

    answers = {**answers, **prompt(template_version_question() + repo_question())}
    repo = answers['repo']

    return {**answers, **prompt(branch_question())}


# SEARCH
def search_interactive():
    return prompt(t_repo_question() + search_depth_question())


# VERSION
def version_interactive():
    return prompt(t_repo_question() + version_depth_question())


def interactive_prompt():

    command = prompt(commands())['command']

    if command == "register":
        return register_interactive()
    elif command == "create":
        return create_interactive()
    elif command == "upgrade":
        return upgrade_interactive()
    elif command == "preview":
        return preview_interactive()
    elif command == "search":
        return search_interactive()
    elif command == "version":
        return version_interactive()
    else:
        print("Command not supported in interactive use")
