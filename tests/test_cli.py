"""Main cli behaviour for archctl"""
import pytest

from click.testing import CliRunner

from archctl.__main__ import main


@pytest.fixture(scope='session')
def cli_runner():
    """Fixture that returns a helper function to run the cookiecutter cli."""
    runner = CliRunner()

    def cli_main(*cli_args, **cli_kwargs):
        """Run cookiecutter cli main with the given args."""
        return runner.invoke(main, cli_args, **cli_kwargs)

    return cli_main


@pytest.fixture(params=['-V', '--version'])
def version_cli_flag(request):
    """Pytest fixture return both version invocation options."""
    return request.param


def test_cli_version(cli_runner, version_cli_flag):
    """Verify Archctl version output by `archctl` on cli invocation."""

    result = cli_runner(version_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith('Archctl')
