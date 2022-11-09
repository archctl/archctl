import shutil
import pathlib

import igittigitt


def get_ignore_parser(path):
    parser = igittigitt.IgnoreParser()
    parser.parse_rule_file(pathlib.Path(path))
    return parser


def move_dir(src_path, dest_path, ignore_path=None):

    # Get all the non dirs in the src_path
    files = [str(file) for file in pathlib.Path(src_path).glob('./**/*') if not file.is_dir()]
    # Get all the dirs in the src_path
    dirs = [str(dir) for dir in pathlib.Path(src_path).glob('./**/*') if dir.is_dir()]

    # Exclude all the files matched by the rules in the ignore file
    if ignore_path is not None:
        parser = get_ignore_parser(ignore_path)
        files = [file for file in files if not parser.match(pathlib.Path((file)))]
        dirs = [dir for dir in dirs if not parser.match(pathlib.Path((dir)))]

    base_path_len = len(src_path.split('/'))

    for dir in dirs:
        distance = len(dir.split('/')) - base_path_len + 1
        relative_path = '/'.join(dir.split('/')[-distance:])
        pathlib.Path(dest_path + relative_path).mkdir(parents=True, exist_ok=True)

    # Move all the not matched files:
    for file in files:
        distance = len(file.split('/')) - base_path_len + 1
        relative_path = '/'.join(file.split('/')[-distance:])
        file_dest_path = dest_path + relative_path
        shutil.move(file, file_dest_path)


def exists(path):
    return pathlib.Path(path).exists()
