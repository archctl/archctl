import pytest
import os

import archctl.user_config as uc

p_repo_1 = {
            "name": "my-org/my-project-repo",
            "def_branch": "main"
        }

p_repo_2 = {
            "name": "my-org/my-other-project",
            "def_branch": "develop"
        }

t_repo_1 = 'my-template-repo'

t_repo_2 = 'my-other-t'


@pytest.fixture(autouse=True)
def set_uc():
    uc.config_path = '/tmp/.archctl'
    uc.create_config_file()
    yield
    os.system('rm /tmp/.archctl')


def test_add_p():

    res1 = uc.add_p_repo(p_repo_1)
    res2 = uc.add_p_repo(t_repo_1)

    config = uc.read_user_config()['p_repos']

    match1 = [x for x in config if x == p_repo_1]
    match2 = [x for x in config if x['name'] == t_repo_1]

    assert res1 is True
    assert len(match1) == 1
    assert res2 is False
    assert len(match2) == 0


def test_add_t():

    res1 = uc.add_t_repo(t_repo_1)
    res2 = uc.add_t_repo(p_repo_1)

    config = uc.read_user_config()['t_repos']

    assert res1 is True
    assert t_repo_1 in config
    assert res2 is False
    assert p_repo_1['name'] not in config


def test_delete_p():
    uc.add_p_repo(p_repo_1)
    uc.add_p_repo(p_repo_2)

    res = uc.delete_p_repo(p_repo_1)

    config = uc.read_user_config()['p_repos']

    match1 = [x for x in config if x == p_repo_1]
    match2 = [x for x in config if x == p_repo_2]

    assert res is True
    assert len(config) == 1
    assert len(match1) == 0
    assert len(match2) == 1


def test_delete_t():
    uc.add_t_repo(t_repo_1)
    uc.add_t_repo(t_repo_2)

    res = uc.delete_t_repo(t_repo_2)

    config = uc.read_user_config()['t_repos']

    assert res is True
    assert len(config) == 1
    assert t_repo_1 in config
    assert t_repo_1 in config


def test_update_p():

    uc.add_p_repo(p_repo_1)

    res1 = uc.update_p_repo(p_repo_1, p_repo_2)
    res2 = uc.update_p_repo(p_repo_2, t_repo_1)
    res3 = uc.update_p_repo(p_repo_1, p_repo_2)

    config = uc.read_user_config()['p_repos']

    match1 = [x for x in config if x == p_repo_1]
    match2 = [x for x in config if x == p_repo_2]
    match3 = [x for x in config if x['name'] == t_repo_1]

    assert res1 is True
    assert res2 is False
    assert res3 is False
    assert len(match1) == 0
    assert len(match2) == 1
    assert len(match3) == 0


def test_update_t():

    uc.add_t_repo(t_repo_1)

    res1 = uc.update_t_repo(t_repo_1, t_repo_2)
    res2 = uc.update_t_repo(t_repo_2, p_repo_1)
    res3 = uc.update_t_repo(t_repo_1, t_repo_2)

    config = uc.read_user_config()['t_repos']

    assert res1 is True
    assert res2 is False
    assert res3 is False
    assert t_repo_1 not in config
    assert t_repo_2 in config
    assert p_repo_1['name'] not in config
