import logging
import pathlib
import re
import shutil
from pprint import pprint

import igittigitt

from archctl.github import GHCli
import archctl.commons as comm

cookiecutter_dir_pattern = re.compile("^(.*\/)*\{\{cookiecutter\..*\}\}$")

logger = logging.getLogger(__name__)


def get_ignore_parser(path):
    parser = igittigitt.IgnoreParser()
    parser.parse_rule_file(path)
    return parser


def move_dir(src_path, dest_path, ignore_path=None):

    # Get the pathlib.Path object of the given paths
    src_path = pathlib.Path(src_path)
    dest_path = pathlib.Path(dest_path)
    if ignore_path is not None:
        ignore_path = pathlib.Path(ignore_path)

    # Get the pathlib.Path object of all the non dirs in the src_path
    files = [file for file in src_path.glob("./**/*") if not file.is_dir()]
    # Get the pathlib.Path object of all the dirs in the src_path
    dirs = [dir for dir in src_path.glob("./**/*") if dir.is_dir()]

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
        file_dest_path = dest_path.joinpath(file.relative_to(src_path))
        shutil.move(file, file_dest_path)


def get_child_folder(path):
    path = pathlib.Path(path)
    return [dir for dir in path.glob("./**/*") if dir.is_dir()][0]


def move_file(src_path, dest_path):
    shutil.move(pathlib.Path(src_path), pathlib.Path(dest_path))


def exists(path):
    return pathlib.Path(path).exists()


def print_diff(name, diff):
    print("-" * 127 + f"\nFile name: {name}")
    if isinstance(diff, list):
        pprint(diff, width=127)
    else:
        for line in diff:
            print(line)
    print("-" * 127)


def print_diffs(diffs, show_add):
    # Print additions
    print("Added files:")
    for addition in diffs["A"]:
        if show_add:
            print_diff(addition["name"], addition["diff"])
        else:
            print("+ " + addition["name"])

    # Print deletions
    print("Deleted files:")
    for addition in diffs["D"]:
        print(f"- {addition}")

    # Print modifications
    print("Modified files:")
    for addition in diffs["M"]:
        print_diff(addition["name"], addition["diff"])


def has_templates(cli: GHCli, ref=None):
    """Returns true if the repo has cookiecutter templates at the given ref"""

    # Get the tree of files recursively, to get all the files in the repo
    # with the lowest amount of info
    tree = cli.get_tree(ref, "1")

    if not tree:
        return False

    for dir in tree["tree"]:
        if dir["mode"] == "040000" and cookiecutter_dir_pattern.match(dir["path"]):
            return True

    return False


def not_relative(path: pathlib.Path, others: list[pathlib.Path]):
    for other in others:
        if path != other and path.is_relative_to(other):
            return False

    return True


def search_templates(cli: GHCli, ref: str | None = None) -> list[comm.Template]:
    """Search for cookiecutter templates in the given repo@ref
    Returns a dictionary where the name of the template is the key and
    the path to the template is the value.
    """

    # Get the tree of files recursively, to get all the files in the repo
    # with the lowest amount of info
    tree = cli.get_tree(ref, "1")

    if not tree:
        return []

    # Get all the directories in the tree that match the cookiecutter project
    # template folder regular expresion --> ^(.*\/)*\{\{cookiecutter\..*\}\}$
    cc_dirs_path = [
        pathlib.Path(dir["path"])
        for dir in tree["tree"]
        if (dir["mode"] == "040000" and cookiecutter_dir_pattern.match(dir["path"]))
    ]

    # Select only the parent cc directories
    paths = [path for path in cc_dirs_path if not_relative(path, cc_dirs_path)]

    if len(paths[0].parts) == 1:  # Root directory contains a cookiecutter template
        return [comm.Template(cli.cw_repo.repo, cli.cw_repo, None)]

    # From that list of dirs, split the path to get all the folder's individual
    # names and select the name of the parent to get the template name
    return [comm.Template(t.parent.name, cli.cw_repo, str(t.parent)) for t in paths]


def __key_exists(dictionary, *keys):
    if not isinstance(dictionary, dict):
        raise AttributeError("keys_exists() expects dict as first argument.")
    if len(keys) == 0:
        raise AttributeError("keys_exists() expects at least two arguments, one given.")
    _dict = dictionary
    for key in keys:
        try:
            _dict = _dict[key]
        except KeyError:
            return False
    return True


def inspect_branch_template(
    search_resul: dict, cli: GHCli, branch, depth, template: comm.Template
):

    branch_commits = []
    if template.template_path is not None:
        branch_commits = cli.get_commits(template.template_path, branch)[:depth]
    else:
        branch_commits = cli.get_commits(sha=branch)[:depth]

    commits = [
        {"message": c["commit"]["message"].split("\n")[0][:60], "sha": c["sha"]}
        for c in branch_commits
    ]

    if __key_exists(search_resul, template.template, "branches", branch):
        search_resul[template.template]["branches"][branch] += commits
    elif __key_exists(search_resul, template.template, "branches"):
        search_resul[template.template]["branches"][branch] = commits
    elif __key_exists(search_resul, template.template):
        search_resul[template.template]["branches"] = {branch: commits}
    else:
        search_resul[template.template] = {"branches": {branch: commits}}

    return search_resul


def inspect_branch(
    search_resul: dict, cli: GHCli, branch, depth, template: comm.Template | None = None
):
    logger.debug(f"Searching for the versions contained in {branch}")

    if template is not None:
        search_resul = inspect_branch_template(
            search_resul, cli, branch, depth, template
        )
    else:
        branch_templates = search_templates(cli, branch)
        for branch_temp in branch_templates:
            search_resul = inspect_branch_template(
                search_resul, cli, branch, depth, branch_temp
            )

    return search_resul


def inspect_tag_template(search_resul: dict, cli: GHCli, tag, template: str):

    if __key_exists(search_resul, template, "tags"):
        if tag["name"] not in search_resul[template]["tags"]:
            search_resul[template]["tags"] += [tag["name"]]
    elif __key_exists(search_resul, template):
        search_resul[template]["tags"] = [tag["name"]]
    else:
        search_resul[template] = {"tags": [tag["name"]]}

    return search_resul


def inspect_tag(
    search_resul: dict, cli: GHCli, tag, template: comm.Template | None = None
):
    logger.debug(f"Searching for the templates contained in {tag}")

    tag_templates = [t.template for t in search_templates(cli, tag["sha"])]

    if template is not None:
        if template.template in tag_templates:
            search_resul = inspect_tag_template(
                search_resul, cli, tag, template.template
            )
    else:
        for tag_temp in tag_templates:
            search_resul = inspect_tag_template(search_resul, cli, tag, tag_temp)

    return search_resul


def print_search(search_resul: dict, tags: bool):
    if search_resul:
        print("The following Templates were found in the specified repo:")
        for t, t_info in search_resul.items():
            print(f"Template -- {t}:")
            if tags:
                print("\tTag Versions:")
                if "tags" in t_info:
                    for tag in t_info["tags"]:
                        print(f"\t\t- {tag}")
                else:
                    print("\t\tNo Tags found in the specified repo")
            else:
                print("\tBranch Versions:")
                for branch, b_info in t_info["branches"].items():
                    print(f"\t\t- {branch}:")
                    for commit in b_info:
                        mssg = commit["message"]
                        sha = commit["sha"][:7]
                        print(f"\t\t\t* [{sha}]: {mssg}")
