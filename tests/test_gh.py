import pytest
import archctl.github as gh


@pytest.fixture()
def test_repo():
    gh.create_repo('archctl', 'test')
