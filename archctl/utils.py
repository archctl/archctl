import pathlib
import shutil
from pprint import pprint

import igittigitt


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


# def diff_dirs(path_1, path_2, ignore_path=None):

#     # Get all the non dirs in the first path
#     files_1 = [file for file in pathlib.Path(path_1).glob('./**/*') if not file.is_dir()]
#     # Get all the non dirs in the second path
#     files_2 = [file for file in pathlib.Path(path_2).glob('./**/*') if not file.is_dir()]

#     # Exclude all the files matched by the rules in the ignore file
#     if ignore_path is not None:
#         parser = get_ignore_parser(ignore_path)
#         files_1 = [file for file in files_1 if not parser.match((file))]
#         files_2 = [file for file in files_2 if not parser.match((file))]

def print_diff(name, diff):
    print('-' * 127 + f'\nFile name: {name}')
    pprint(diff, width=127)
    print('-' * 127)
