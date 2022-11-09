"""Main cli behaviour for archctl"""
import pytest
import os

from click.testing import CliRunner

from archctl.__main__ import main
import archctl.user_config as uc
import archctl.github as gh


@pytest.fixture(scope='session')
def cli_runner():
    """Fixture that returns a helper function to run the cookiecutter cli."""
    runner = CliRunner()

    def cli_main(*cli_args, **cli_kwargs):
        """Run cookiecutter cli main with the given args."""
        return runner.invoke(main, cli_args, **cli_kwargs)

    return cli_main


@pytest.fixture(scope='session', autouse=True)
def setup_repo():
    gh.create_repo('archctl/test')
    gh.create_dir('archctl/test', '{{cookiecutter.project_slug}}/test')
    gh.create_repo('archctl/test2')
    gh.create_dir('archctl/test2', '{{cookiecutter.project_slug}}/test')


@pytest.fixture(scope='session', autouse=True)
def set_uc():
    uc.config_path = '/tmp/.archctl/.archctl'
    uc.create_config_file()
    uc.add_p_repo({'name': 'test_p', 'def_branch': 'main'})
    uc.add_t_repo('archctl/test')
    yield
    os.system('rm -rf /tmp/.archctl/')


@pytest.fixture(params=['-V', '--version'])
def version_cli_flag(request):
    """Return both version invocation options."""
    return request.param


@pytest.fixture(params=['-y', '--yes'])
def yes_flags(request):
    """Pytest fixture return both version depth invocation options."""
    return request.param


@pytest.fixture(params=['-v', '--verbose'])
def verbose_flags(request):
    """Pytest fixture return both version depth invocation options."""
    return request.param


def test_archctl_version(cli_runner, version_cli_flag):
    """Verify Archctl version output by `archctl` on cli invocation."""

    result = cli_runner(version_cli_flag)

    assert result.exit_code == 0
    assert result.output.startswith('Archctl')


@pytest.fixture(params=['-d', '--depth'])
def depth_flags(request):
    """Pytest fixture return both version depth invocation options."""
    return request.param


def test_version_1(cli_runner, depth_flags):
    """Verify Archctl version output by `archctl` on cli invocation."""

    res1 = cli_runner('version', 'archctl/test', depth_flags, '1')
    res2 = cli_runner('version', 'archctl/test', depth_flags, '-2')
    res3 = cli_runner('version', 'archctl/test', depth_flags, '-1')

    assert res1.output.startswith('These are the values')
    assert res2.output.startswith('Usage:')
    assert res3.output.startswith('These are the values')


def test_version_2(cli_runner):
    """Verify Archctl version output by `archctl` on cli invocation."""

    res1 = cli_runner('version', 'archctl/test')
    res2 = cli_runner('version', 'wrong/repo')

    assert res1.output.startswith('These are the values')
    assert res2.output.startswith('Usage:')


def test_search_1(cli_runner, depth_flags):
    """Verify Archctl version output by `archctl` on cli invocation."""

    res1 = cli_runner('search', 'archctl/test', depth_flags, '1')
    res2 = cli_runner('search', 'archctl/test', depth_flags, '-2')
    res3 = cli_runner('search', 'archctl/test', depth_flags, '-1')

    assert res1.output.startswith('These are the values')
    assert res2.output.startswith('Usage:')
    assert res3.output.startswith('These are the values')


def test_search_2(cli_runner):
    """Verify Archctl version output by `archctl` on cli invocation."""

    res1 = cli_runner('search', 'archctl/test')
    res2 = cli_runner('search', 'wrong/repo')

    assert res1.output.startswith('These are the values')
    assert res2.output.startswith('Usage:')


@pytest.fixture(params=['-k', '--kind'])
def kind_flags(request):
    """Pytest fixture return both version depth invocation options."""
    return request.param


@pytest.fixture(params=['-b', '--branch'])
def branch_flags(request):
    """Pytest fixture return both version depth invocation options."""
    return request.param


def test_register_kind(cli_runner, kind_flags):

    # Registering a P repo that exists in gh, not in local config with the correct kind
    res1 = cli_runner('register', 'archctl/archctl', kind_flags, 'Project')
    # Registering a P repo that exists in gh, not in local config with the wrong kind
    res2 = cli_runner('register', 'archctl/archctl', kind_flags, 'Template')
    # Registering a T repo that exists in gh, not in local config with the correct kind
    res3 = cli_runner('register', 'archctl/test2', kind_flags, 'Template')
    # Registering a T repo that exists in gh, not in local config with the wrong kind
    res4 = cli_runner('register', 'archctl/test2', kind_flags, 'Project')

    assert res1.output.startswith('These are the values')
    assert "['-b', '--branch']: main" in res1.output
    assert res2.output.startswith('Given kind of the repo')
    assert res3.output.startswith('These are the values')
    assert res4.output.startswith('Given kind of the repo')


def test_register_branch(cli_runner, branch_flags):

    # Register a P repo with a correct branch
    res1 = cli_runner('register', 'archctl/archctl', branch_flags, 'main')
    # Register a T repo with a correct branch
    res2 = cli_runner('register', 'archctl/test2', branch_flags, 'main')
    # Register a repo with a wrong branch
    res3 = cli_runner('register', 'archctl/archctl', branch_flags, 'wrong_branch')

    assert res1.output.startswith('These are the values')
    assert "['-k', '--kind']: Project" in res1.output
    assert res1.output.startswith('These are the values')
    assert "['-k', '--kind']: Template" in res2.output
    assert res3.output.startswith('Usage:')


def test_register_repo(cli_runner):
    # Register a P repo that exists in gh but not in local config
    res1 = cli_runner('register', 'archctl/archctl')
    # Register a T repo that exists in gh but not in local config
    res2 = cli_runner('register', 'archctl/test2')
    # Register a repo that exists in gh and in local config
    res3 = cli_runner('register', 'archctl/test')
    # Register a repo that doesn't exist in gh
    res4 = cli_runner('register', 'archctl/test')

    assert res1.output.startswith('These are the values')
    assert "['-k', '--kind']: Project" in res1.output
    assert res2.output.startswith('These are the values')
    assert "['-k', '--kind']: Template" in res2.output
    assert res3.output.startswith('Usage:')
    assert res4.output.startswith('Usage:')
