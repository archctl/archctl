"""Main cli behaviour for archctl"""
import pytest

from click.testing import CliRunner

from archctl.__main__ import main

_exit_code = None


@pytest.fixture(scope='session')
def cli_runner():
    """Fixture that returns a helper function to run the cookiecutter cli."""
    runner = CliRunner()

    def cli_main(*cli_args, **cli_kwargs):
        """Run cookiecutter cli main with the given args."""
        return runner.invoke(main, cli_args, **cli_kwargs)

    return cli_main


# @pytest.fixture(params=['y', 'n'])
# def confirmation(request):
#     """Return yes and no to confirmation prompt. To be used as input"""
#     # If user says y, exit code should be 0
#     # If user says n, exit code should be 1
#     global _exit_code
#     if request.param == 'y':
#         _exit_code=0
#     elif request.param == 'n':
#         _exit_code=1

#     return request.param


@pytest.fixture(params=['-V', '--version'])
def version_cli_flag(request):
    """Return both version invocation options."""
    return request.param


def test_archctl_version(cli_runner, version_cli_flag):
    """Verify Archctl version output by `archctl` on cli invocation."""

    result = cli_runner(version_cli_flag)

    assert result.exit_code == 0
    assert result.output.startswith('Archctl')


@pytest.fixture(params=['-I', '--interactive'])
def interactive_cli_flag(request):
    """Return both interactive invocation options."""
    return request.param


# def test_archctl_interactive(cli_runner, interactive_cli_flag):
#     """Verify Archctl interactive options show the prompt."""

#     result = cli_runner(interactive_cli_flag)

#     # Click Runner doesn't support InquirerPy's terminal UI
#     assert str(result.exception) == ('Stdin is not a terminal.')


@pytest.fixture(params=['-d', '--depth'])
def depth_flags(request):
    """Pytest fixture return both version depth invocation options."""
    return request.param


@pytest.fixture(params=['-1', '4'])
def depth_values(request):
    """Pytest fixture return both version depth invocation options."""
    return request.param


def test_version(cli_runner, depth_flags, depth_values):
    """Verify Archctl version output by `archctl` on cli invocation."""

    result = cli_runner('version', 'dktunited/soivre', depth_flags, depth_values)

    assert result.output.startswith('These are the values')


def test_search(cli_runner, depth_flags, depth_values):
    """Verify Archctl version output by `archctl` on cli invocation."""

    result = cli_runner('search', 'dktunited/soivre', depth_flags, depth_values)

    assert result.output.startswith('These are the values')
