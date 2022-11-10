import git
import pprint


def clone_repo(repo, path):
    return git.Repo.clone_from(f'git@github.com:{repo[0]}/{repo[1]}.git', path)


def git_push_changes(repo, path, message):
    repo.git.add(path)
    repo.index.commit(message)
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

    # Your last commit of the current branch
    commit_feature = repo.head.commit.tree

    # Your last commit of the dev branch
    commit_origin_dev = repo.commit(f'origin/{branch}')
    new_files = []
    deleted_files = []
    modified_files = []

    # Comparing
    diff_index = commit_origin_dev.diff(commit_feature)

    # Collection all new files
    for file in diff_index.iter_change_type('A'):
        new_files.append(file)

    # Collection all deleted files
    for file in diff_index.iter_change_type('D'):
        deleted_files.append(file)

    # Collection all modified files
    for file in diff_index.iter_change_type('M'):
        modified_files.append(file)

    print('Added Files:')
    pprint.pprint(new_files)
    print('Delented Files:')
    pprint.pprint(deleted_files)
    print('Modified Files:')
    pprint.pprint(modified_files)
