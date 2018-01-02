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
    output = subprocess.check_output(['i3parse', 'bindings', config_file])
    assert output == b"""\
default mod+t mode "test"
test q mode "default"
"""

def test_executable():
    # Ensure that args are read correctly
    config_file = os.path.join(HERE, 'config1')
    output = subprocess.check_output(['i3parse', 'free', '--config', config_file])
    assert output.startswith(b'Mod+a')

def test_free():
    config_file = os.path.join(HERE, 'config1')
    output = subprocess.check_output(['i3parse', 'free', '--config', config_file])
    assert output.startswith(b'Mod+a\nMod+Shift+a\nMod+Control+a\nMod+Mod1+a')
    assert len(output.splitlines()) == 464 # consistency testing

def test_free_letter_sort():
    config_file = os.path.join(HERE, 'config1')
    output = subprocess.check_output(['i3parse', 'free', '--config', config_file, 'hey'])
    print(output)
    assert output.startswith(b'Mod+h')
    assert output.index(b'Mod+h')  < output.index(b'Mod+e') < output.index(b'Mod+y')
