# make code as python 3 compatible as possible
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import os

import parsimonious.grammar

DEFAULT_FILE = os.path.join(os.environ['HOME'], '.i3/config')

PARSER = argparse.ArgumentParser(description='')
parsers = PARSER.add_subparsers(dest='command')
binding_parser = parsers.add_parser('bindings', help='Show bindings')
binding_parser.add_argument('file', type=str, help='', nargs='?', default=DEFAULT_FILE)

def main():
    args = PARSER.parse_args()
    if args.command == 'bindings':
        with open(args.file) as stream:
            input_string = stream.read()
            parse(input_string)
    else:
        raise ValueError(args.bindings)


def parse(input):
    grammar = parsimonious.grammar.Grammar(r'''
result = ( block / line ) *
i3_toggle_fullscreen = "fullscreen" space "toggle"

bind_action = exec_action / i3_toggle_fullscreen / mode_action / focus_action / i3_action / i3_move_action / i3_split_action / i3_layout_action / i3_toggle_float / i3_workspace_command / i3_resize_action / scratch_show
block = mode_block / bar_block
mode_block = "mode" space quoted_string quote_block
bar_block = "bar" space quote_block
quote_block = ( space ? ) "{" newline lines ( space ? ) "}" newline

window_event = "for_window" space window_specifier space bind_action
window_specifier = "[" comma_list "]"
comma_list = key_value / (comma_list space "," space key_value)
key_value = variable "=" quoted_string


lines = line *
line = comment / statement
statement = ( space * ) statement_no_line newline
statement_no_line = bind_statement / force_wrapping / set_statement / status_command / font_statement / float_key_statement / workspace_buttons / popup_fullscreen_action / exec_action / window_event / empty_statement

popup_fullscreen_action = "popup_during_fullscreen" space popup_action

exec_action = exec quoted_string

popup_action = "leave_fullscreen" / "smart" / "ignore"

workspace_buttons = "workspace_buttons" space yes_no

empty_statement = ""
bind_statement = "bindsym" (space "--release") ? space key space bind_action
key = word

scratch_show = "scratchpad" space "show"
scratch_hide = "scratchpad" space "hide"


status_command = "status_command" space any_chars
i3_move_action = "move" ( space ("container" / "window" / "workspace") space "to" space ("output" / "mark" / "workspace") ) ? space move_target
move_target = direction / "scratchpad" / number
i3_workspace_command = "workspace" space (quoted_string / workspace_sentinels / number)
workspace_sentinels = "back_and_forth"
i3_toggle_float = "floating" space "toggle"
i3_layout_action = "layout" space layout
layout = "stacking" / "tabbed" / "default" / ( "toggle" space "split" )
mode_action = "mode" space quoted_string
focus_action = "focus" ( space "output" ) ? space (direction / focus_mode / focus_location)
focus_mode = "mode_toggle"
focus_location = "parent" / "child"
direction = "left" / "right" / "up" / "down"
i3_action = "kill" / "fullscreen" / "reload" / "restart" / "exit"
i3_split_action = "split" space split_direction
split_direction = "h" / "v"
i3_resize_action = "resize" space ( "shrink" / "grow" ) space ("width" / "height") space measurement

exec_action = "exec " exec_bash
exec_bash = any_chars
float_key_statement = "floating_modifier " word
comment = (space ?) octo any_chars newline
font_statement = "font " any_chars
any_chars = ~".*"
octo = ~"\#"
newline = ~"\n*"
force_wrapping = "force_focus_wrapping" space yes_no
yes_no = "yes" / "no"
space = ~"[ \t]+"
set_statement = "set " word " " word
word = ~"[^() \n]+"
variable = ~"[a-zA-Z_]*"

quoted_string = quote string_contents quote
string_contents = ~'[^"\n]*'
quote = "\""

measurement = ((axiomatic_measurement space "or" space measurement) / axiomatic_measurement)
axiomatic_measurement = number space ("ppt" / "px")
number = ~"[0-9]+"
''')

    result = grammar.parse(input)
    #dump_tree(result)
    bindings = get_bindings(result)
    sort_key = lambda k: (k['mode'], k['key'])
    for binding in sorted(bindings, key=sort_key):
        print(binding['mode'], binding['key'], binding['action_text'])

def get_bindings(ast, mode_name=None):
    if ast.expr_name == 'mode_block':
        _, _, mode_name_node, _ = ast.children
        _, mode_name, _ = [c.text for c in mode_name_node.children]


    if ast.expr_name == 'bind_statement':
        return [parse_binding(ast, mode_name)]
    else:
        bindings = []
        for child in ast.children:
            bindings.extend(get_bindings(child, mode_name))
        return bindings

def parse_binding(ast, mode_name):
    _, release, _, key_node, _, action = ast.children
    key = key_node.text
    i3_complex_action = move_command = i3_action = mode = command = None
    action_text = action.text
    specific_action, = action.children
    if specific_action.expr_name == 'exec_action':
        _exec, bash_exec = specific_action
        command = bash_exec.text
    elif specific_action.expr_name == 'i3_move_action':
        move_command = 'blah'
    elif specific_action.expr_name == 'i3_split_action':
        _, _, direction = specific_action
        i3_complex_action = dict(action='split', direction=direction.text)
    elif specific_action.expr_name == 'mode_action':
        _, _, (_,  string , _) = specific_action.children
        mode = string.text
    elif specific_action.expr_name == 'focus_action':
        _, _, output, direction = specific_action.children
        i3_complex_action = dict(output=output.text, direction=direction.text, action='focus')
    elif specific_action.expr_name == 'i3_action':
        i3_action = specific_action.text
    elif specific_action.expr_name == 'i3_toggle_float':
        i3_action = 'toggle_float'
    elif specific_action.expr_name == 'i3_layout_action':
        _, _, layout = specific_action.children
        i3_complex_action = dict(action='layout', layout=layout.text)
    elif specific_action.expr_name == 'i3_workspace_command':
        _, _, workspace = specific_action.children
        workspace_target, = workspace.children
        workspace_target_name = workspace_name = None
        if workspace_target.expr_name == 'quoted_string':
            _, workspace_name, _ = workspace_target.children
        elif workspace_target.expr_name == 'number':
            workspace_name = int(workspace_target.text)
        elif workspace_target.expr_name == 'workspace_sentinels':
            workspace_target_name = workspace_target.text
        else:
            raise ValueError(workspace_target.expr_name)
        i3_complex_action = dict(
            action='workspace',
            workspace=workspace_name,
            workspace_target=workspace_target_name)
    elif specific_action.expr_name == 'i3_resize_action':
        i3_complex_action = dict(action='resize')
    elif specific_action.expr_name == 'scratch_show':
        i3_action = 'show_scratchpad'
    elif specific_action.expr_name == 'i3_toggle_fullscreen':
        i3_action = 'toggle_fullscreen'
    else:
        raise ValueError(specific_action.expr_name)

    release = bool(release.text.strip())
    return dict(
        key=key,
        command=command,
        target_mode=mode,
        i3_action=i3_action,
        i3_complex_action=i3_complex_action,
        action_text=action_text,
        text=ast.text,
        release=release,
        mode=mode_name,
        )



def dump_tree(ast, depth=0):
    print('    ' * depth + ast.expr_name)
    for x in ast.children:
        dump_tree(x, depth=depth+1)
