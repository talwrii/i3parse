import os
import subprocess

import mock

import i3parse.i3parse

HERE = os.path.dirname(__file__)


def test_files():
    with mock.patch('os.environ', dict(HOME='/home/user')):
        assert i3parse.i3parse.default_configs() == [
            '/home/user/.i3/config', '/home/user/.config/i3/config',
            '/etc/i3/config', '/etc/xdg/i3/config']

    with mock.patch('os.environ', dict(
            HOME='/home/user',
            XDG_CONFIG_HOME='/xdg_home',
            XDG_CONFIG_DIRS='/xdg_dirs')):
        assert i3parse.i3parse.default_configs() == [
            '/home/user/.i3/config', '/xdg_home/i3/config',
            '/etc/i3/config', '/xdg_dirs/i3/config']

def test_run():
    subprocess.check_output(["i3parse", "--help"])

def test_consistency():
    config_file = os.path.join(HERE, 'config1')
    output = run(['bindings', config_file])
    assert output == """\
default mod+t mode "test"
test q mode "default"
"""

def test_executable():
    # Ensure that args are read correctly
    config_file = os.path.join(HERE, 'config1')
    output = run(['free', '--config', config_file])
    assert output.startswith('Mod+a')

def test_free():
    config_file = os.path.join(HERE, 'config1')
    output = run(['free', '--config', config_file])
    assert output.startswith('Mod+a\nMod+Shift+a\nMod+Control+a\nMod+Mod1+a')
    assert len(output.splitlines()) == 464 # consistency testing

def test_free_letter_sort():
    config_file = os.path.join(HERE, 'config1')
    output = run(['free', '--config', config_file, 'hey'])
    assert output.startswith('Mod+h')
    assert output.index('Mod+h')  < output.index('Mod+e') < output.index('Mod+y')

def run(args):
    return '\n'.join(i3parse.i3parse.run(args)) + '\n'

