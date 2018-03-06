"""
Special file to bootstrap py.test fixtures and other test dependencies
"""
import os
import sys
import pytest

HERE = os.path.abspath(os.path.dirname(__file__))

# add project to the python path
sys.path.insert(0, os.path.dirname(HERE))


@pytest.fixture(scope='session')
def test_dir():
    """Root test folder, useful to find fixtures or other required files inside the test folder."""
    return HERE
