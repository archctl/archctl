


def is_repo(repo):
    # FILL WITH REPO VALIDATION LOGIC
    return True


def validate_repo(ctx, param, value):
    if is_repo(value):
        return value

    raise click.BadParameter("Repo must be either owner/name or a valid GitHub URL")

