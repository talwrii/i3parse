# i3parse
A functional but not feature-complete parser for [i3wm's](https://github.com/i3/i3) config file. Originally written for the purposes of querying keybindings, but it can likely quickly be patched to support new features.

# Usage

```
# List keybindings
> i3parse bindings

```

# Caveats
This code is a violation of [don't repeat yourself](http://wiki.c2.com/?DontRepeatYourself).
i3 defines a specification for its configuration file in [its source code](https://github.com/mariusmuja/i3wm/blob/dfcc65ab8dd8ff9b995c8f970424454342f8be2e/parser-specs/config.spec); we duplicate a different specification here which is liable to be invalidated by changes to i3's specification.
The author deemed that parsing this file (which is in a custom language that is parsed by a custom PERL script) was more effort that the costs of dealing with duplication, given that the configuration file is unlikely to change.

This parser was derived from features in the author's configuration file, rather than from i3's configuration file specification. As such, it may fail to parse your configuration but can likely quickly be patched to support new features.

# Debugging
In the case of parse errors, the author has found it helpful to copy the error-causing configuration and repeatedly delete lines until a minimal error-causing configuration is found. The grammar rules can then be reordered so that the most specific rule that should match is being used (the first rule in the grammar definition is the rule that the input file should match). Rules can further be commented out with `#` and replaced with even simpler rules. Having such a minimised problem helps one debug.

`test.sh` runs some course tests (ensuring installation works and *i3parse* runs on sample input).
