import git


def clone_repo(repo, path):
    return git.Repo.clone_from(f'git@github.com:{repo[0]}/{repo[1]}.git', path)


def git_push_changes(repo, path, message):
    repo.git.add(path)
    repo.index.commit(message)
    repo.git.push()
