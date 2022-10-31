"""Interactive questions for the main CLI commands."""

from InquirerPy import prompt

from archctl.validation import (validate_repo_interactive,
                                validate_repo_name_available_interactive,
                                validate_depth_interactive,
                                validate_t_version_interactive)

#  GLOBAL VARIABLES
repo = ''
t_repo = ''
template = ''
last_three = ''


# GITHUB FUNCTIONS, SUBSTITUTE IN THE FUTURE FOR THE ONES IN GIHTUB MODULE
def get_repo_branches(repo):
    # Get the branches through the API
    return ['develop', 'main']


def get_available_templates(repo):
    # Get the templates through the GitHub API
    return ['java', 'php', 'vuejs']


def get_last_three_v(repo, template):
    # Get the last three commits for that template through the GitHub API
    global last_three
    last_three = ['7485a1fd', '5442332399', 'd5f05c84e4fd']
    return last_three


# GETTER FUNCTIONS FOR GLOBAL VARS
def get_repo():
    return repo


def get_t_repo():
    return t_repo


def get_template():
    return template


def get_last_three():
    return last_three


# QUESTIONS
commands = [
    {
        'type': 'list',
        'name': 'command',
        'message': 'What command do you wish to perform?:',
        'choices': ['register', 'create', 'upgrade', 'preview', 'search', 'version']
    }
]

repo_question = [
    {
        'type': 'input',
        'name': 'repo',
        'message': 'Name of the repository (owner/name or URL):',
        'validate': validate_repo_interactive
    }
]

kind_question = [
    {
        'type': 'list',
        'name': 'kind',
        'message': 'Kind of repository:',
        'choices': ['Project', 'Template']
    }
]

name_question = [
    {
        'type': 'input',
        'name': 'name',
        'message': 'Name of the project that will be created:',
        'validate': validate_repo_name_available_interactive
    }
]

t_repo_question = [
    {
        'type': 'input',
        'name': 't_repo',
        'message': 'Name or URL of the Template\'s repository:',
        'validate': validate_repo_interactive
    }
]

branch_question = [
    {
        'type': 'list',
        'name': 'branch',
        'message': 'Branch of the repository to checkout from:',
        'choices': get_repo_branches(get_repo())
    }
]

template_question = [
    {
        'type': 'list',
        'name': 'template',
        'message': 'Template to render in the project:',
        'choices': lambda templates: get_available_templates(get_t_repo())
    }
]

template_version_question = [
    {
        'type': 'input',
        'name': 't_version',
        'message': ('Version of the template to use. (Last three: ' +
                    ' '.join(get_last_three_v(get_t_repo(), get_template())) + '):'),
        'default': lambda default: get_last_three()[0],
        'validate': (lambda t_version: validate_t_version_interactive(get_t_repo(), get_template(), t_version))
    }
]

search_depth_question = [
    {
        'type': 'input',
        'name': 'depth',
        'message': ('Depth of the search for each branch\n(number of' +
                    'commits/versions on each branch on each template) -1 to show all:'),
        'default': '3',
        'validate': validate_depth_interactive
    }
]

version_depth_question = [
    {
        'type': 'input',
        'name': 'depth',
        'message': 'Number of renders to show info about, -1 to show all:',
        'default': '5',
        'validate': validate_depth_interactive
    }
]

confirm_question = [
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

    answers = prompt(repo_question + kind_question)
    repo = answers['repo']

    return {**answers, **prompt(branch_question)}


# CREATE
def create_interactive():
    global t_repo, template

    answers = prompt(name_question + t_repo_question)
    t_repo = answers['t_repo']

    answers = {**answers, **prompt(template_question)}
    template = answers['template']

    return {**answers, **prompt(template_version_question)}


# UPGRADE
def upgrade_interactive():
    global t_repo, template, repo

    answers = prompt(t_repo_question)
    t_repo = answers['t_repo']

    answers = {**answers, **prompt(template_question)}
    template = answers['template']

    answers = {**answers, **prompt(template_version_question)}

    print('\n-------------------------------------------------------------')
    print('Now, please enter one or more project repositories to upgrade!')
    print('-------------------------------------------------------------\n')

    confirm = True
    projects = []

    while confirm:

        project = prompt(repo_question)
        repo = project['repo']

        projects.append({**project, **prompt(branch_question)})

        confirm = prompt(confirm_question)['confirm']

    answers['projects'] = projects
    return answers


# PREVIEW
def preview_interactive():
    global t_repo, template, repo

    answers = prompt(t_repo_question)
    t_repo = answers['t_repo']

    answers = {**answers, **prompt(template_question)}
    template = answers['template']

    answers = {**answers, **prompt(template_version_question + repo_question)}
    repo = answers['repo']

    return {**answers, **prompt(branch_question)}


# SEARCH
def search_interactive():
    return prompt(t_repo_question + search_depth_question)


# VERSION
def version_interactive():
    return prompt(t_repo_question + version_depth_question)


def interactive_prompt():

    command = prompt(commands)['command']

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
