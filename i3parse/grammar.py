# -*- coding: utf-8 -*-

import parsimonious.grammar

def build_grammar():
    grammar = parsimonious.grammar.Grammar(r'''
result = ( block / line ) *
i3_toggle_fullscreen = "fullscreen" space "toggle"

block = mode_block / bar_block
bar_block = "bar" space quote_block
quote_block = ( space ? ) "{" newline (lines / colors_block) ( space ? ) "}" newline
mode_block = "mode" space (quoted_variable / quoted_string) quote_block
colors_block = "colors" space quote_block


lines = line*
line = comment / statement
statement = ( space * ) statement_no_line newline
statement_no_line = bind_statement / geometry_statement / mouse_warping_statement / workspace_layout / workspace_statement / yes_no_statement / set_statement / status_command / font_statement / float_key_statement / workspace_buttons / popup_fullscreen_action / exec_always / exec_action / window_event / assign_statement / no_focus_statement / orientation_statement / new_float_border / new_window_border / hide_edge_borders_statement / set_from_resource / gaps_statement / smart_gaps_statement / smart_borders_statement / empty_statement

workspace_statement = "workspace" space workspace_const space workspace_option
workspace_option = workspace_output / gaps_statement 
workspace_output = "output" space word 
yes_no_statement =  ( "workspace_auto_back_and_forth" / "force_focus_wrapping" / "focus_follows_mouse" / "force_xinerama") space yes_no

gaps_statement = "gaps" space gaps_orientation_const space number

smart_gaps_statement = "smart_gaps" space ( yes_no / "on" / "off" / "inverse_outer")
smart_borders_statement = "smart_borders" space ( "no_gaps" / yes_no / "on" / "off")

window_event = "for_window" space window_specifier space bind_action
window_specifier = "[" ( comma_list ) "]"
comma_list = (key_value space ("," space)? comma_list) / key_value
key_value = variable_name "=" quoted_string
mouse_warping_statement = "mouse_warping" space ( "none" / "output" )


assign_statement = "assign" space window_specifier space ("→" space)? workspace_const
no_focus_statement = "no_focus" space window_specifier

hide_edge_borders_statement = "hide_edge_borders" space window_edge_const

window_edge_const = "none" / "vertical" / "horizontal" / "both" / "smart_no_gaps" / "smart"
gaps_orientation_const = "inner" / "outer" / "horizontal" / "vertical" / "top" / "left" / "bottom" / "right"

geometry_statement = ("floating_minimum_size" / "floating_maximum_size") space signed_number (space?) "x" (space?) signed_number

workspace_layout = "workspace_layout" space layout

new_float_border = "new_float" space border_const
new_window_border = "new_window" space border_const
border_const = ( "normal" / "none" / ("pixel" space number) )

orientation_statement = "default_orientation" space orientation
orientation = ("vertical" / "horizontal" / "auto" )

popup_fullscreen_action = "popup_during_fullscreen" space popup_action

exec_action = exec space rest

exec_always = "exec_always" space rest

popup_action = "leave_fullscreen" / "smart" / "ignore"

workspace_buttons = "workspace_buttons" space yes_no

empty_statement = space*
bind_statement = ( "bindsym" / "bindcode" ) (space bind_option)*  space key (space bind_option)* space bind_actions

bind_option = "--release" / "--border" / "--whole-window" / "--exclude-titlebar"

bind_actions = (bind_action space ?  ("," / ";") space ? bind_actions) / bind_action
bind_action = exec_action / i3_toggle_fullscreen / mode_action / focus_action / i3_action / i3_move_action / i3_split_action / i3_layout_action / i3_modify_float / i3_modify_stick / i3_workspace_command / i3_resize_action / scratch_show / border_action / gaps_action

border_action = "border" space border_const

gaps_action = "gaps" space gaps_orientation_const space gaps_action_focus space gaps_action_change space number 
gaps_action_focus = "current" / "all"
gaps_action_change = "set" / "plus" / "minus" / "toggle"

key = word

scratch_show = "scratchpad" space "show"
scratch_hide = "scratchpad" space "hide"

status_command = "status_command" space any_chars
i3_move_action = "move" (space ("container" / "window" / "workspace") ) ? ( space  "to" ) ? ( space ( "output" / "mark" / "workspace" ) ) ? space move_target
move_target = direction / "scratchpad" / number
i3_workspace_command = "workspace" space workspace_const
workspace_const = (quoted_string /  workspace_sentinels / variable_name / number)
workspace_sentinels = "back_and_forth"
i3_modify_float = "floating" space ( "enable" / "toggle" / "disable") (space "border" space "pixel" space number)?
i3_modify_stick = "sticky" space ( "enable" / "toggle" / "disable") 
i3_layout_action = "layout" space layout
layout = "stacking" / "tabbed" / "default" / ( "toggle" space "split" )
focus_action = "focus" ( space "output" ) ? space (direction / focus_mode / focus_location)
focus_mode = "mode_toggle"
focus_location = "parent" / "child"
direction = "left" / "right" / "up" / "down"
i3_action = "kill" / "fullscreen" / "reload" / "restart" / "exit"
i3_split_action = "split" space split_direction
split_direction = "vertical" / "horizontal" / "toggle" / "h" / "v"
i3_resize_action = "resize" space ( "shrink" / "grow" ) space ("width" / "height") space measurement

exec_action = "exec " exec_bash
mode_action = "mode" space (quoted_string  / variable_name / variable )
exec_bash = any_chars
float_key_statement = "floating_modifier " word
comment = (space ?) octo any_chars newline
font_statement = "font " any_chars
any_chars = ~".*"
octo = ~"\#"
newline = ~"\n*"
yes_no = "yes" / "no"
space = ~"[ \t]+"
set_statement = "set " ( word / variable ) " " rest
set_from_resource = "set_from_resource" space variable space dotted_name space rest
word = ~"[^() \n]+"
rest = ~"[^\n]+"
dotted_name =  ( variable_name "." dotted_name ) / variable_name
variable_name = ~"[a-zA-Z_][a-zA-Z_0-9]*"
variable = "$" variable_name


quoted_variable = quote variable quote

quoted_string = quote string_contents quote
string_contents = ~'[^"\n]*'
quote = "\""

measurement = ((axiomatic_measurement space "or" space measurement) / axiomatic_measurement)
axiomatic_measurement = number space ("ppt" / "px")
number = ~"[0-9]+"
signed_number = ( "-" ? ) number
''')
    return grammar
