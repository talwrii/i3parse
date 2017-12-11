# make code as python 3 compatible as possible
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import collections
import itertools
import json
import os

import graphviz
import parsimonious.grammar

DEFAULT_FILE = os.path.join(os.environ['HOME'], '.i3/config')

def file_option(parser):
    parser.add_argument('file', type=str, help='', nargs='?', default=DEFAULT_FILE)

def json_option(parser):
    parser.add_argument('--json', action='store_true', help='Output in machine readable json')

def build_parser():
    parser = argparse.ArgumentParser(description='')
    parsers = parser.add_subparsers(dest='command')

    modes = parsers.add_parser('modes', help='Show the keybinding modes and how to traverse them')
    file_option(modes)

    mode_graph = parsers.add_parser('mode-graph', help='Show the keybinding modes and how to traverse them')
    file_option(mode_graph)
    mode_graph.add_argument('--drop-key', '-d', help='Ignore this key in all modes', type=str, action='append')
    mode_graph.add_argument('--unicode', '-u', action='store_true', default=False, help='Compress with unicode')

    validate_parser = parsers.add_parser('validate', help='Validate key-bindings file (check if it parses)')
    file_option(validate_parser)

    binding_parser = parsers.add_parser('bindings', help='Show bindings')
    file_option(binding_parser)
    binding_parser.add_argument('--mode', '-m', type=str, help='Only should bindings for this mode')
    binding_parser.add_argument('--type', '-t', type=str, choices=sorted(set(get_bind_types().values())), help='Only show bindings of this type')
    json_option(binding_parser)
    return parser

def mode_graph(ast, ignore_keys=None):
    if ignore_keys is None:
        ignore_keys = set()
    ignore_keys = set(ignore_keys)

    modes = get_modes(ast)
    graph = collections.defaultdict(list)

    for mode in modes:
        graph[mode] = []

    bindings = get_bindings(ast)
    for b in bindings:
        if b['type'] == 'mode':
            if b['key'] in ignore_keys:
                continue
            graph[b['mode']].append((b['key'], b['mode_target']))
    return graph

def compress_binding(binding):
    output = binding.lower()
    output = output.replace('$mod', '$')
    output = output.replace('mod1', 'M')
    output = output.replace('super', 'S')
    output = output.replace('shift', 's')
    return output

def dump_graph(graph, key_formatter=compress_binding):
    graphviz_graph = graphviz.Digraph()
    for node, neighbours in graph.items():
        graphviz_graph.node(node)
        for k, neighbour in neighbours:
            graphviz_graph.edge(node, neighbour, label=key_formatter(k))
    return graphviz_graph.source

def diacriticize_binding(s):
    "'Creatively' compress binding with diacritics"
    parts = s.split('+')
    key = parts[-1].lower()
    shift = modifier = sup = mod1 = False
    for part in parts[:-1]:
        if part.lower() == 'mod1':
            mod1 = True
        if part == 'S':
            sup = True
        if part.lower() == '$mod':
            modifier = True
        if part.lower() == 'shift':
            shift = True

    combining_s = u"\u1de4"
    subscript_m = u'\u2098'

    output = key
    if shift:
        output = output.upper()
    if sup:
        output = output + super_s
    if mod1:
        output = output + subscript_m
    if modifier:
        output = '$' + output

    return output


def main():
    args = build_parser().parse_args()
    if args.command == 'mode-graph':
        with open(args.file) as stream:
            input_string = stream.read()
            ast = parse(input_string)

        graph = mode_graph(ast, ignore_keys=args.drop_key)
        key_formatter = diacriticize_binding if args.unicode else compress_binding
        print(dump_graph(graph, key_formatter))
    elif args.command == 'modes':
        with open(args.file) as stream:
            input_string = stream.read()
            ast = parse(input_string)

        for mode in sorted(get_modes(ast)):
            print(mode)
    elif args.command == 'validate':
        with open(args.file) as stream:
            input_string = stream.read()
            ast = parse(input_string)
    elif args.command == 'bindings':
        with open(args.file) as stream:
            input_string = stream.read()
            ast = parse(input_string)

        # dump_tree(ast)

        bindings = get_bindings(ast)
        sort_key = lambda k: (k['mode'], k['key'])
        for binding in sorted(bindings, key=sort_key):
            if args.mode and args.mode != binding['mode']:
                continue

            if args.type is not None:
                if binding['type'] != args.type:
                    continue

            if args.json:
                workspace = (binding.get('i3_complex_action') or dict()).get('workspace')
                data = dict(mode=binding['mode'], key=binding['key'], text=binding['action_text'], action_type=binding['type'], line=binding['line'])
                if workspace is not None:
                    data['workspace'] = workspace
                print(json.dumps(data))
            else:
                print(binding['mode'], binding['key'], binding['action_text'])

    else:
        raise ValueError(args.bindings)

def build_grammar():
    grammar = parsimonious.grammar.Grammar(r'''
result = ( block / line ) *
i3_toggle_fullscreen = "fullscreen" space "toggle"

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
statement_no_line = bind_statement / force_wrapping / focus_follows_mouse /  set_statement / status_command / font_statement / float_key_statement / workspace_buttons / popup_fullscreen_action / exec_action / window_event / empty_statement

popup_fullscreen_action = "popup_during_fullscreen" space popup_action

exec_action = exec quoted_string

popup_action = "leave_fullscreen" / "smart" / "ignore"

workspace_buttons = "workspace_buttons" space yes_no

empty_statement = ""
bind_statement = "bindsym" (space "--release") ? space key space bind_action
bind_action = exec_action / i3_toggle_fullscreen / mode_action / focus_action / i3_action / i3_move_action / i3_split_action / i3_layout_action / i3_toggle_float / i3_workspace_command / i3_resize_action / scratch_show

key = word

scratch_show = "scratchpad" space "show"
scratch_hide = "scratchpad" space "hide"

status_command = "status_command" space any_chars
i3_move_action = "move" (space ("container" / "window" / "workspace") ) ? ( space  "to" ) ? ( space ( "output" / "mark" / "workspace" ) ) ? space move_target
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
focus_follows_mouse = "focus_follows_mouse" space yes_no
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
    return grammar

def parse(input_string):
    grammar = build_grammar()
    return grammar.parse(input_string)

_get_bind_types = None
def get_bind_types():
    global _get_bind_types
    if _get_bind_types is None:
        ACTION_TYPES = dict(
            exec_action='exec',
            i3_toggle_fullscreen='window',
            mode_action='mode',
            focus_action='window',
            i3_action='window',
            i3_move_action='window',
            i3_split_action='window',
            i3_layout_action='window',
            i3_toggle_float='window',
            i3_workspace_command='workspace',
            i3_resize_action='window',
            scratch_show='window',
        )
        grammar = build_grammar()
        actions = [m.name for m in grammar['bind_action'].members]
        found_types = set(ACTION_TYPES[a] for a in actions)
        if found_types != set(ACTION_TYPES.values()):
            raise ValueError(found_types - set(ACTION_TYPES.values()))
        _get_bind_types = ACTION_TYPES

    return _get_bind_types


def get_modes(ast):
    if ast.expr_name == 'mode_block':
        _, _, name_node, _ = ast.children
        if name_node.expr_name == 'quoted_string':
            _, string_node, _ = name_node
            return [string_node.text]
        else:
            raise ValueError(name_node.expr_name)
    else:
        return list(itertools.chain.from_iterable(get_modes(child) for child in ast.children))



def get_bindings(ast, mode_name='default'):
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
    bind_types = get_bind_types()
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
            workspace_name = workspace_name.text
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
        type=bind_types[specific_action.expr_name],
        i3_action=i3_action,
        i3_complex_action=i3_complex_action,
        action_text=action_text,
        text=ast.text,
        release=release,
        mode_target=mode,
        mode=mode_name,
        )


def dump_tree(ast, depth=0):
    print('    ' * depth + ast.expr_name)
    for x in ast.children:
        dump_tree(x, depth=depth+1)
