import logging
import pathlib
import re
import shutil
from pprint import pprint

import igittigitt

from archctl.github import GHCli

cookiecutter_dir_pattern = re.compile('^(.*\/)*\{\{cookiecutter\..*\}\}$')

logger = logging.getLogger(__name__)


def get_ignore_parser(path):
    parser = igittigitt.IgnoreParser()
    parser.parse_rule_file(path)
    return parser


def move_dir(src_path, dest_path, ignore_path=None):

    # Get the pathlib.Path object of the given paths
    src_path = pathlib.Path(src_path)
    dest_path = pathlib.Path(dest_path)
    ignore_path = pathlib.Path(ignore_path)

    # Get the pathlib.Path object of all the non dirs in the src_path
    files = [file for file in src_path.glob('./**/*') if not file.is_dir()]
    # Get the pathlib.Path object of all the dirs in the src_path
    dirs = [dir for dir in src_path.glob('./**/*') if dir.is_dir()]

    # Exclude all the files matched by the rules in the ignore file
    if ignore_path is not None:
        parser = get_ignore_parser(ignore_path)
        files = [file for file in files if not parser.match((file))]
        dirs = [dir for dir in dirs if not parser.match((dir))]

    for dir in dirs:
        relative_path = dir.relative_to(src_path)
        dest_path.joinpath(relative_path).mkdir(parents=True, exist_ok=True)

    # Move all the not matched files:
    for file in files:
        file_dest_path = dest_path.join(file.relative_to(src_path))
        shutil.move(file, file_dest_path)


def exists(path):
    return pathlib.Path(path).exists()


def print_diff(name, diff):
    print('-' * 127 + f'\nFile name: {name}')
    pprint(diff, width=127)
    print('-' * 127)


def print_diffs(diffs):
    # Print additions
    print('Added files:')
    for addition in diffs['A']:
        print_diff(addition['name'], addition['diff'])

    # Print deletions
    print('Deleted files:')
    for addition in diffs['D']:
        print(f'-{addition}')

    # Print modifications
    print('Modified files:')
    for addition in diffs['M']:
        print_diff(addition['name'], addition['diff'])


def has_templates(repo, ref=None):
    """Returns true if the repo has cookiecutter templates at the given ref"""

    cli = GHCli()
    cli.cw_repo = repo

    # Get the tree of files recursively, to get all the files in the repo
    # with the lowest amount of info
    tree = cli.get_tree(ref, '1')

    if not tree:
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

    cli = GHCli()
    cli.cw_repo = repo

    # Get the tree of files recursively, to get all the files in the repo
    # with the lowest amount of info
    tree = cli.get_tree(ref, '1')

    if not tree:
        return False

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
