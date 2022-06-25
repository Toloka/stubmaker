import os

import pytest
import subprocess

from functools import partial
from setuptools import findall


TEST_DIR = os.path.dirname(__file__)
STUBMAKER_CMD = 'stubmaker'

# Returns paths relative to test_package
get_input_path = partial(os.path.join, TEST_DIR, 'test_package')

# Returns paths relative to expected_stubs
get_expected_stub = partial(os.path.join, TEST_DIR, 'expected_stubs')


@pytest.fixture(scope='session')
def get_output_path(tmpdir_factory):
    """Applies stubmaker and returns results dir"""
    output_path = str(tmpdir_factory.mktemp('output'))
    process = subprocess.run(
        [
            STUBMAKER_CMD,
            '--module-root', 'test_package',
            '--src-root', get_input_path(),
            '--output-dir', output_path,
            '--objects-aliases', os.path.join(TEST_DIR, 'test_objects_aliases.py'),
            '--modules-aliases', os.path.join(TEST_DIR, 'test_modules_aliases.json'),
        ],
        stderr=subprocess.PIPE, text=True,
    )
    if process.returncode != 0:
        assert process.stderr == ''
        raise subprocess.CalledProcessError(process.returncode, process.args)
    return partial(os.path.join, output_path)


def get_module_paths():
    input_path = get_input_path()
    return [os.path.relpath(path, input_path) for path in findall(input_path) if path.endswith('.py')]


@pytest.mark.parametrize('module_path', get_module_paths())
def test_generated_stub_file_is_same(module_path, get_output_path):
    with open(get_output_path(module_path + 'i')) as stub_file:
        with open(get_expected_stub(module_path + 'i')) as expected_stub:
            assert expected_stub.read() == stub_file.read()
