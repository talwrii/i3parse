import os
import subprocess

import mock

import i3parse.i3parse

HERE = os.path.dirname(__file__)


def test_files():
    with mock.patch('os.environ', dict(HOME='/home/user')):
        assert i3parse.i3parse.default_files() == ['/home/user/.i3/config', '/home/user/.config/i3/config', '/etc/i3/config', '/etc/xdg/i3/config']

    with mock.patch('os.environ', dict(
            HOME='/home/user',
            XDG_CONFIG_HOME='/xdg_home',
            XDG_CONFIG_DIRS='/xdg_dirs')):
        assert i3parse.i3parse.default_files() == ['/home/user/.i3/config', '/xdg_home/i3/config', '/etc/i3/config', '/xdg_dirs/i3/config']

def test_run():
    subprocess.check_output(["i3parse", "--help"])

def test_consistency():
    config_file = os.path.join(HERE, 'config1')
    output = subprocess.check_output(['i3parse', 'bindings', config_file])
    assert output == b"""\
default mod+t mode "test"
test q mode "default"
"""
