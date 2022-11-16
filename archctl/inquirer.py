"""Interactive questions for the main CLI commands."""

import logging

from InquirerPy import prompt

# import archctl.commons as comm
# import archctl.main as arch
# import archctl.user_config as uc
# import archctl.utils as util
# import archctl.validation as val
# from archctl.github import GHCli
import archctl.commands as cmd

logger = logging.getLogger(__name__)


COMMANDS = {
    'register': cmd.Register(),
    'list': cmd.List(),
    'delete': cmd.Delete(),
    'create': cmd.Create(),
    # 'upgrade': cmd.Upgrade(),
    # 'preview': cmd.Preview(),
    # 'search': cmd.Search(),
    # 'version': cmd.Version()
}

# #  GLOBAL VARIABLES
# REPO = None
# PROJECT_REPOS = None
# TEMPLATE_REPO = None
# TEMPLATE_REPOS = None
# TEMPLATE = None
# TEMPLATES = None

# CLI = GHCli()

# ANOTHER_REPO = 'Do you want to add another REPO?'
# DEF_BRANCHES = 'Do you want to continue with this configuration?'
# MORE_REPOS = 'Do you wish to add more repos manually?'


# def print_info(message):
#     print('\n-------------------------------------------------------------')
#     print(message)
#     print('-------------------------------------------------------------\n')


# def list_branch_names():
#     """Returns a list with the names of the branches in the given REPO"""
#     if REPO is not None:
#         CLI.cw_repo = REPO
#         branches = [branch['name'] for branch in CLI.list_branches()]
#         if branches:
#             return branches
#         else:
#             return []
#     else:
#         return []


# def get_available_templates():
#     """Sets the global variable paths to contain the paths of all"""

#     global TEMPLATES
#     TEMPLATES = utils.search_templates(TEMPLATE_REPO)

#     if TEMPLATES:
#         return TEMPLATES
#     else:
#         return []


# def get_last_three_v():
#     # Get the last three commits for that TEMPLATE through the GitHub API
#     path = TEMPLATES[TEMPLATE]
#     commits = gh.get_commit(TEMPLATE_REPO, path=path)[:3]
#     if commits:
#         last_three = [t_version['sha'][:8] for t_version in commits]
#     else:
#         last_three = []
#     return last_three


# def get_t_repos():
#     t_repos = [repo for repo in TEMPLATE_REPOS]
#     t_repos.append('Other')
#     return t_repos


# def get_p_repos():
#     p_repos = [repo['name'] for repo in PROJECT_REPOS]
#     return p_repos


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


# def repo_input_question():
#     return [
#         {
#             'type': 'input',
#             'name': 'repo',
#             'message': 'Name of the repository (owner/name or URL):',
#             'validate': lambda res: val.validate_repo_interactive(res),
#             "invalid_message": "Repository not found in Github.com"
#         }
#     ]


# def repo_config_question():
#     return [
#         {
#             'type': 'input',
#             'name': 'repo',
#             'message': 'Name of the repository (owner/name or URL):',
#             'validate': lambda res: val.validate_repo_interactive(res),
#             "invalid_message": "Repository not found in Github.com"
#         }
#     ]


# def register_repo_question():
#     return [
#         {
#             'type': 'input',
#             'name': 'repo',
#             'message': 'Name of the repository (owner/name or URL):',
#             'validate': lambda res: val.validate_register_repo_interactive(res),
#             "invalid_message": "Repository not found in Github.com or already registered"
#         }
#     ]


# def config_repo_question():
#     return [
#         {
#             'type': 'list',
#             'name': 'old_repo',
#             'message': 'Name of the repository (owner/name) to be modified:',
#             'choice': get_p_repos(),
#             'validate': lambda res: val.validate_local_repo_interactive(res),
#             "invalid_message": "Repository not found in local config"
#         }
#     ]


# def repos_checkbox_question():
#     return [
#         {
#             'type': 'checkbox',
#             'name': 'selected_repos',
#             'message': 'Select the Project repos to update from local config:',
#             'choices': get_p_repos(),
#             'validate': val.validate_repos_checkbox,
#             'invalid_message': 'Should be at least 1 selection',
#             'instruction': '(Please, select at least 1 repository)',
#         }
#     ]


# def kind_question():
#     return [
#         {
#             'type': 'list',
#             'name': 'kind',
#             'message': 'Kind of repository:',
#             'choices': ['Project', 'Template'],
#             'validate': lambda res: val.validate_kind_interactive(REPO, res),
#             'invalid_message': 'No TEMPLATES found in the repository'
#         }
#     ]


# def name_question():
#     return [
#         {
#             'type': 'input',
#             'name': 'name',
#             'message': 'Name of the project that will be created\n'
#                     '(If no org is indicated, the REPO will be created under the logged user account):',
#             'validate': lambda res: val.validate_repo_name_available_interactive(res),
#             "invalid_message": "Repository already exists"
#         }
#     ]


# def t_repo_question():
#     return [
#         {
#             'type': 'input',
#             'name': 'template_repo',
#             'message': 'Name or URL of the Template\'s repository (owner/name or URL):',
#             'validate': lambda res: val.validate_t_repo_interactive(res)
#         }
#     ]


# def t_repo_config_question():
#     return [
#         {
#             'type': 'list',
#             'name': 'template_repo',
#             'message': 'Select a Template REPO from your config:',
#             'choices': get_t_repos()
#         }
#     ]


# def branch_question():
#     return [
#         {
#             'type': 'list',
#             'name': 'branch',
#             'message': 'Branch of the repository to checkout from:',
#             'choices': list_repo_branches()
#         }
#     ]


# def template_question():
#     return [
#         {
#             'type': 'list',
#             'name': 'template',
#             'message': 'Template to render in the project:',
#             'choices': get_available_templates()
#         }
#     ]


# def template_version_question():
#     return [
#         {
#             'type': 'input',
#             'name': 'template_version',
#             'message': ('Version of the TEMPLATE to use. (Last three: ' + str(get_last_three_v()) + '):'),
#             'validate': (lambda t_version: val.validate_t_version_interactive(TEMPLATE_REPO, TEMPLATE, t_version))
#         }
#     ]


# def search_depth_question():
#     return [
#         {
#             'type': 'input',
#             'name': 'depth',
#             'message': 'Depth of the search for each branch\n(number of'
#                     'commits/versions on each branch on each TEMPLATE) -1 to show all:',
#             'default': '3',
#             'validate': val.validate_depth_interactive
#         }
#     ]


# def version_depth_question():
#     return [
#         {
#             'type': 'input',
#             'name': 'depth',
#             'message': 'Number of renders to show info about, -1 to show all:',
#             'default': '5',
#             'validate': val.validate_depth_interactive
#         }
#     ]


# def confirm_question(message):
#     return [
#         {
#             'type': 'confirm',
#             'message': message,
#             'name': 'confirm',
#             'default': True,
#         }
#     ]


# # PROMPTS FOR TEMPLATE REPO
# def prompt_t_repo_manually():
#     global TEMPLATE_REPO

#     TEMPLATE_REPO = prompt(t_repo_question())['template_repo']


# def prompt_t_repo_from_config():
#     global TEMPLATE_REPO

#     TEMPLATE_REPO = prompt(t_repo_config_question())['template_repo']

#     if TEMPLATE_REPO == 'Other':
#         prompt_t_repo_manually()


# def prompt_t_repo():
#     """If there are tempalte repos stored in local config, prompt those
#         if there are not, prompt the user to input it manually
#     """
#     global TEMPLATE_REPOS

#     # Gets all the TEMPLATE repos in local config
#     TEMPLATE_REPOS = uc.get_t_repos()

#     if TEMPLATE_REPOS:  # If there are TEMPLATE repos in local config
#         prompt_t_repo_from_config()
#     else:  # If there aren't TEMPLATE repos in local config
#         prompt_t_repo_manually()


# def prompt_p_repo_manually():
#     global REPO

#     # Prompt the REPO
#     REPO = prompt(repo_question())['repo']
#     # Prompt the branch from the given REPO
#     branch = prompt(branch_question())['branch']
#     # Add the given REPO and branch to the answer
#     return {'repo': REPO, 'branch': branch}


# # PROMPT FOR PROJECT REPOS
# def prompt_p_repos_manually():
#     global PROJECT_REPOS

#     print_info('Please enter one or more project repositories to upgrade!\n\t\t\t\t(One by One)')

#     # Loop to prompt for a REPO and branch, one by one
#     continue_ = True
#     while continue_:
#         PROJECT_REPOS.append(prompt_p_repo_manually())
#         # Prompt for continuation
#         continue_ = prompt(confirm_question(ANOTHER_REPO))['confirm']


# def prompt_p_repo_from_config():
#     global PROJECT_REPOS, REPO, OTHER

#     # Prompt to select which repos of the config user wants to upgrade
#     question = repos_checkbox_question()
#     question[0]['choices'].append('Other')
#     selected_p_repos = prompt(question)['selected_repos']

#     if 'Other' in selected_p_repos:
#         selected_p_repos.pop(selected_p_repos.index('Other'))
#         OTHER = True

#     # Get a list with all the info of the Project repos the user selected
#     PROJECT_REPOS = [{'repo': REPO['name'], 'branch': REPO['def_branch']}
#                      for REPO in PROJECT_REPOS if REPO['name'] in selected_p_repos]

#     # Prompt user to confirm if he wants to proceed with the stored config or modify it
#     print_info('These are the def branches setup in local config:\n' + str(PROJECT_REPOS))
#     continue_ = prompt(confirm_question(DEF_BRANCHES))['confirm']

#     if not continue_:  # If user says yes, PROJECT_REPOS holds all the info as a global var

#         # When user indicates no, question which branch of the REPO the user
#         # whishes to use in each REPO
#         print_info('Please select the default branch for each of the selected projects')

#         for p_repo in PROJECT_REPOS:
#             REPO = p_repo['name']
#             new_p_repo = {'repo': p_repo['name'], 'branch': prompt(branch_question())['branch']}
#             PROJECT_REPOS[PROJECT_REPOS.index(p_repo)] = new_p_repo

#         # Now, p_repo holds all the info as a global var


# def prompt_p_repos_from_config():
#     global PROJECT_REPOS, REPO, OTHER

#     # Prompt to select which repos of the config user wants to upgrade
#     question = repos_checkbox_question()
#     question[0]['choices'].append('Other')
#     selected_p_repos = prompt(question)['selected_repos']

#     if 'Other' in selected_p_repos:
#         selected_p_repos.pop(selected_p_repos.index('Other'))
#         OTHER = True

#     # Get a list with all the info of the Project repos the user selected
#     PROJECT_REPOS = [{'repo': REPO['name'], 'branch': REPO['def_branch']}
#                      for REPO in PROJECT_REPOS if REPO['name'] in selected_p_repos]

#     # Prompt user to confirm if he wants to proceed with the stored config or modify it
#     print_info('These are the def branches setup in local config:\n' + str(PROJECT_REPOS))
#     continue_ = prompt(confirm_question(DEF_BRANCHES))['confirm']

#     if not continue_:  # If user says yes, PROJECT_REPOS holds all the info as a global var

#         # When user indicates no, question which branch of the REPO the user
#         # whishes to use in each REPO
#         print_info('Please select the default branch for each of the selected projects')

#         for p_repo in PROJECT_REPOS:
#             REPO = p_repo['name']
#             new_p_repo = {'repo': p_repo['name'], 'branch': prompt(branch_question())['branch']}
#             PROJECT_REPOS[PROJECT_REPOS.index(p_repo)] = new_p_repo

#         # Now, p_repo holds all the info as a global var


# def prompt_p_repos():
#     """ Prompt user to select the projects to update from local config
#         and optionally, add more manually
#     """
#     global PROJECT_REPOS

#     # Get the Project Repos stored in the user config
#     PROJECT_REPOS = uc.get_p_repos()

#     if PROJECT_REPOS:  # If there are Project repos stored in the config
#         prompt_p_repos_from_config()

#         # If user selected other
#         if OTHER:
#             prompt_p_repos_manually()
#         # else:  # If user didn't select other
#         #     continue_ = prompt(confirm_question(MORE_REPOS))['confirm']
#         #     if continue_:
#         #         prompt_p_repos_manually()
#     else:  # If there are no Project repos stored in the config
#         prompt_p_repos_manually()


# # REGISTER
# def register_interactive():
#     global REPO

#     answers = prompt(register_repo_question())
#     REPO = answers['repo']

#     answers = {**answers, **prompt(kind_question())}

#     if answers['kind'] == 'Template':
#         return {**answers, **{'branch': None}}
#     else:
#         return {**answers, **prompt(branch_question())}


# # DELETE
# def delete_interactive():
#     answers = {}
#     answers['repo_to_delete'] = prompt(modify_repo_question())['old_repo']
#     return answers


# # DELETE
# def modify_interactive():

#     answers = prompt(modify_repo_question())

#     print_info('Now, please enter the infomation to update')

#     return {**answers, **register_interactive()}


# # CREATE
# def create_interactive():
#     global TEMPLATE

#     answers = prompt(name_question())

#     prompt_t_repo()

#     answers['template_repo'] = TEMPLATE_REPO

#     answers = {**answers, **prompt(template_question())}
#     TEMPLATE = answers['template']

#     return {**answers, **prompt(template_version_question())}


# # UPGRADE
# def upgrade_interactive():
#     global TEMPLATE

#     answers = {}

#     prompt_p_repos()
#     answers['projects'] = PROJECT_REPOS

#     prompt_t_repo()
#     answers['template_repo'] = TEMPLATE_REPO

#     answers = {**answers, **prompt(template_question())}
#     TEMPLATE = answers['template']

#     answers = {**answers, **prompt(template_version_question())}
#     return answers


# # PREVIEW
# def preview_interactive():
#     global TEMPLATE, REPO

#     REPO = prompt(register_repo_question())['repo']
#     branch = prompt(branch_question())['branch']

#     answers = {}
#     answers['repo'] = {'repo': REPO, 'branch': branch}

#     prompt_t_repo()
#     answers['template_repo'] = TEMPLATE_REPO

#     answers = {**answers, **prompt(template_question())}
#     TEMPLATE = answers['template']

#     answers = {**answers, **prompt(template_version_question())}
#     return answers


# # SEARCH
# def search_interactive():

#     answers = {}

#     prompt_t_repo()
#     answers['template_repo'] = TEMPLATE_REPO

#     return {**answers, **prompt(search_depth_question())}


# # VERSION
# def version_interactive():

#     answers = {}

#     prompt_t_repo()
#     answers['template_repo'] = TEMPLATE_REPO

#     return {**answers, **prompt(version_depth_question())}


def interactive_prompt():

    command = prompt(commands())['command']

    com = COMMANDS[command]

    com.run()
