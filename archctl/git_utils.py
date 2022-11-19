import difflib
from pathlib import Path

import git

import archctl.commons as comm


def clone_repo(repo: comm.Repo, path):
    return git.Repo.clone_from(repo.ssh_url, path)


def commit_changes(repo, path, message):
    repo.git.add(path)
    repo.index.commit(message)


def push_changes(repo, path, message):
    commit_changes(repo, path, message)
    repo.git.push()


def checkout(repo, new_branch):

    branch = [b for b in repo.branches if b.name == new_branch]
    if len(branch) == 0:
        branch = repo.create_head(new_branch)  # create new branch if none exists
    else:
        branch = branch[0]

    branch.checkout()


def publish_branch(repo, branch):
    repo.git.push('--set-upstream', 'origin', branch)


def diff_branches(repo, branch):

    # The last commit in the current branch
    commit_feature = repo.head.commit.tree

    # The last commit in the target branch
    commit_origin_dev = repo.commit(f'origin/{branch}')

    # Get the iterator with all the diffs between both commits
    diff_index = commit_origin_dev.diff(commit_feature)

    # Differ for generating the diff strings
    differ = difflib.Differ()

    # Collection all new files
    added = []
    for diff in diff_index.iter_change_type('A'):
        # Get the content of the blob of the newly created file
        blob = diff.b_blob.data_stream.read().decode('utf-8').splitlines()

        # Get the name of the file
        name = Path(diff.b_path).name

        # Get the changes to the file as diff
        difference = list(differ.compare('', blob))

        # Add the dictionary with the name and diff to the list of added files
        added.append({'name': name, 'diff': difference})

    # Collection all deleted files
    deleted = []
    for diff in diff_index.iter_change_type('D'):

        # Get the name of the file
        name = Path(diff.a_path).name

        deleted.append(name)

    # Collection all modified files
    modified = []
    for diff in diff_index.iter_change_type('M'):
        # Get the contents of the blobs
        a_content = diff.a_blob.data_stream.read().decode('utf-8').splitlines()
        b_content = diff.b_blob.data_stream.read().decode('utf-8').splitlines()

        # Get the name of the file
        name = Path(diff.b_path).name

        difference = difflib.context_diff(a_content, b_content, Path(diff.a_path).name, Path(diff.b_path).name)

        #difference = [line for line in list(differ.compare(a_content, b_content)) if (line.startswith('+') or line.startswith('-'))]

        modified.append({'name': name, 'diff': difference})

    return {'A': added, 'D': deleted, 'M': modified}
