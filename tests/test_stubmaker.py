import os
import pytest
import subprocess

from functools import partial
from setuptools import findall


try:
    from yatest.common import binary_path, source_path
except ImportError:
    TEST_DIR = os.path.dirname(__file__)
    STUBMAKER_CMD = 'stubmaker'
else:
    TEST_DIR = source_path('library/python/stubmaker/tests')
    STUBMAKER_CMD = binary_path('library/python/stubmaker/stubmaker')


# Returns paths relative to test_package
get_input_path = partial(os.path.join, TEST_DIR, 'test_package')

# Returns paths relative to expected_stubs
get_expected_stub = partial(os.path.join, TEST_DIR, 'expected_stubs')


@pytest.fixture(scope='session')
def get_output_path(tmpdir_factory):
    """Applies stubmaker and returns restults dir"""
    output_path = str(tmpdir_factory.mktemp('output'))
    subprocess.call([
        STUBMAKER_CMD,
        '--module-root', 'test_package',
        '--src-root', get_input_path(),
        '--output-dir', output_path,
    ])
    return partial(os.path.join, output_path)


def get_module_paths():
    input_path = get_input_path()
    return [os.path.relpath(path, input_path) for path in findall(input_path) if path.endswith('.py')]


@pytest.mark.parametrize('module_path', get_module_paths())
def test_generated_stub_file_is_same(module_path, get_output_path):
    with open(get_output_path(module_path + 'i')) as stub_file:
        with open(get_expected_stub(module_path + 'i')) as expected_stub:
            assert expected_stub.read() == stub_file.read()
