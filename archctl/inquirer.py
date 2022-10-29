"""Interactive questions for the main CLI commands."""
from PyInquirer import prompt, Separator


######### REGISTER #########
register = [
    {
        'type': 'input',
        'name': 'repo',
        'message': 'Name of the repository (owner/name or URL):',
        'validate': True # is_repo(val)
    },
    {
        'type': 'list',
        'name': 'kind',
        'message': 'Kind of repository:',
        'choices': ['Project', 'Template']
    }
]

def get_repo_branches(repo):
    # Get the branches through the API
    global branches
    branches = ['develop', 'main']

def register_interactive():
    answers = prompt(register)
    get_repo_branches(answers['repo'])
    default_branch = [
        {
            'type': 'list',
            'name': 'branch',
            'message': 'Default branch of the repository:',
            'choices': branches
        }
    ]
    return {**answers, **prompt(default_branch)}
############################


########## CREATE ##########
create = [
    {
        'type': 'input',
        'name': 'name',
        'message': 'Name of the project that will be created:',
        'validate': True # !repo_exists(val)
    },
    {
        'type': 'input',
        'name': 't_repo',
        'message': 'Name or URL of the Template\'s repository:',
        'validate': True # repo_exists(val)
    }
]

def get_available_templates(repo):
    # Get the templates through the API
    global templates
    templates = ['java', 'php', 'vuejs']

def get_last_three_versions(repo, template):
    # Get the last three commits for that template through the GitHub API
    global template_versions
    template_versions = ['7485a1fd (latest)', '5442332399', 'd5f05c84e4fd']

def create_interactive():
    answers = prompt(create)
    get_available_templates(answers['t_repo'])
    template = [
        {
            'type': 'list',
            'name': 'template',
            'message': 'Template to render in the project:',
            'choices': templates
        }
    ]
    answers = {**answers, **prompt(template)}

    versions = get_last_three_versions(answers['t_repo'], answers['template'])
    template_version = [
        {
            'type': 'input',
            'name': 't_version',
            'message': 'Version of the tempalte to use \n (Last three: ' + ' '.join(template_versions) + '):',
            'default': template_versions[0],
            'validate': True # repo_exists(val)
        }
    ]
    
    return {**answers, **prompt(template_version)}
############################


########## UPGRADE #########
upgrade = [
        {
        'type': 'input',
        'name': 't_repo',
        'message': 'Name or URL of the Template\'s repository:',
        'validate': True # repo_exists(val)
        }
]

def upgrade_interactive():
    answers = prompt(upgrade)
    get_available_templates(answers['t_repo'])
    template = [
        {
            'type': 'list',
            'name': 'template',
            'message': 'Template to render in the project:',
            'choices': templates
        }
    ]
    answers = {**answers, **prompt(template)}

    versions = get_last_three_versions(answers['t_repo'], answers['template'])
    template_version = [
        {
            'type': 'input',
            'name': 't_version',
            'message': 'Version of the tempalte to use \n (Last three: ' + ' '.join(template_versions) + ').',
            'default': template_versions[0],
            'validate': True # repo_exists(val)
        }
    ]
    
    answers = {**answers, **prompt(template_version)}

    print('\n-------------------------------------------------------------')
    print('Now, please enter one or more project repositories to upgrade!')
    print('-------------------------------------------------------------\n')

    stop = False
    projects = []

    while not stop:
        project_repo = [
            {
                'type': 'input',
                'name': 'p_repo',
                'message': 'Name or URL of the Project\'s repository:',
                'validate': True # repo_exists(val)
            }
        ]
        project = prompt(project_repo)

        get_repo_branches(project['p_repo'])
        default_branch = [
            {
                'type': 'list',
                'name': 'branch',
                'message': 'Branch of the Project Repository to checkout from:',
                'choices': branches
            }
        ]
        projects.append({**project, **prompt(default_branch)})

        stop_question = [
            {
                'type': 'confirm',
                'message': 'Do you want to add another repo to upgrade?',
                'name': 'continue',
                'default': True,
            }
        ]
        stop = not prompt(stop_question)['continue']

    answers['projects'] = projects
    return answers
############################


########## PREVIEW #########
def preview_interactive():
    answers = prompt(upgrade)
    get_available_templates(answers['t_repo'])
    template = [
        {
            'type': 'list',
            'name': 'template',
            'message': 'Template to render in the project:',
            'choices': templates
        }
    ]
    answers = {**answers, **prompt(template)}

    versions = get_last_three_versions(answers['t_repo'], answers['template'])
    template_version = [
        {
            'type': 'input',
            'name': 't_version',
            'message': 'Version of the tempalte to use \n (Last three: ' + ' '.join(template_versions) + '):',
            'default': template_versions[0],
            'validate': True # repo_exists(val)
        }
    ]
    answers = {**answers, **prompt(template_version)}

    project_repo = [
        {
            'type': 'input',
            'name': 'p_repo',
            'message': 'Name or URL of the Project\'s repository:',
            'validate': True # repo_exists(val)
        }
    ]
    answers = {**answers, **prompt(project_repo)}

    get_repo_branches(answers['p_repo'])
    default_branch = [
        {
            'type': 'list',
            'name': 'branch',
            'message': 'Branch of the Project Repository to checkout from:',
            'choices': branches
        }
    ]
    return {**answers, **prompt(default_branch)}
############################


########## SEARCH ##########
search = [
    {
        'type': 'input',
        'name': 't_repo',
        'message': 'Name or URL of the Template\'s repository:',
        'validate': True # repo_exists(val)
    },
    {
        'type': 'input',
        'name': 'depth',
        'message': 'Depth of the search for each branch\n(number of commits/versions on each branch on each template)',
        'default': '3', 
        'validate': True # is_natural_number()
    }
]

def search_interactive():
    return prompt(search)
############################


########## VERSION #########
version = [
    {
        'type': 'input',
        'name': 't_repo',
        'message': 'Name or URL of the Templates repository:',
        'validate': True # repo_exists(val)
    },
    {
        'type': 'input',
        'name': 'depth',
        'message': 'Depth of the search for each branch\n(number of commits/versions on each branch on each template)',
        'default': '5',
        'validate': True # is_natural_number()
    }
]

def version_interactive():
    return prompt(version)
############################


def interactive_prompt():
    commands = [
        {
            'type': 'list',
            'name': 'command',
            'message': 'What command do you wish to perform?:',
            'choices': ['register', 'create', 'upgrade', 'preview', 'search', 'version']
        }
    ]
    answer = prompt(commands)

    if answer['command'] == "register":
        return register_interactive()
    elif answer['command'] == "create":
        return create_interactive()
    elif answer['command'] == "upgrade":
        return upgrade_interactive()
    elif answer['command'] == "preview":
        return preview_interactive()
    elif answer['command'] == "search":
        return search_interactive()
    elif answer['command'] == "version":
        return version_interactive()
    else:
        print("Command not supported in interactive use")