# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import re
import sys
import argparse
import io

re_dot_special = re.compile(r"""
(?P<before>^|\ |\n|\(|\{)
(?P<content>
\\\w+?|             #\word.. b
\\vec\ \w|          #\vec p.. b
\\vec\{[^\{\}]+\} #\vec{abc}.. b. no nested {} because that's impossible in regex
)
(?P<dot_type>\.|\.\.)
(?=$|\ |\n|,|\)|\})
""", re.VERBOSE)

re_dot_normal = re.compile(r"""
(?P<before>^|\ |\n|\(|\{)
(?P<content>\w+?)
(?P<dot_type>\.|\.\.)
(?=$|\ |\n|,|\)|\})
""", re.VERBOSE)

re_frac = re.compile(r"""
(?<=\\frac)
\ +?
(?P<nom>[^\ \{\}\n]+?)
\ +?
(?P<denom>[^\ \{\}\n]+?)
(?=$|\ |\n|,)
""", re.VERBOSE)

re_cdot = re.compile(r"""
(?<!\^)           # no ^ before to save complex conjugation
\*                # the *
(?P<wspace>\ *)   # whitespace
(?P<after>[\w\\]) # alphanum + \ for greek letters
""", re.VERBOSE)

re_dots = re.compile(r"""
(?<!\.)           # no dot before
\.{3}             # ...
(?!\.)            # no dot after
(?P<wspace>\ *)   # whitespace
(?P<after>.)      # what comes after
""", re.VERBOSE)

re_braket_full = re.compile(r"""
<(?P<con>
[^\|<>]+
\|
[^\|<>]+
(?:
  \|[^\|<>]+ #optional middle
|)
)>
""", re.VERBOSE)

re_braket_ketbra = re.compile(r"""
(?:
    \|(?P<ket_c>[^\|\ {}<>]+)>
)
(?P<between>\ *)
(?:
    <(?P<bra_c>[^\|\ <>]+)\|
)
""", re.VERBOSE)

re_braket_ket = re.compile(r"""
(?P<before>^|\ |\n|\(|\{)
(?P<ket>
    \|(?P<ket_c>[^\|\ {}<>]+)>
)
(?P<after>$|\ |\n|\)|\})
""", re.VERBOSE)

re_braket_bra = re.compile(r"""
(?P<before>^|\ |\n|\(|\{)
(?P<bra>
    <(?P<bra_c>[^\|\ {}<>]+)\|
)
(?P<after>$|\ |\n|\)|\})
""", re.VERBOSE)

re_sub_superscript_aggressive = re.compile(r"""
(?P<operator>[_\^]) # ^ or _

(?P<before> # optional whitespace before
  \ *?
)

(?P<content>
    [a-zA-Z0-9+\-\*\=,]{2,}  # alphanum, +-*=
)

(?P<after>
  $|\ |\n|\)|\||\^|\_|}
)
""", re.VERBOSE)

re_sub_superscript_conservative = re.compile(r"""
(?P<operator>[_\^]) # ^ or _
(?P<before>\ +?) # whitespace before
(?P<content>
  (?:
    [a-zA-Z0-9+\-\*=]
  |
    ,[a-zA-Z0-9]
  ){2,} # two or more, otherwise no brackets needed
)
(?P<after>\ +?) # whitespace after
""", re.VERBOSE)

re_label_comments = re.compile(r"""
(
(?:\\label\{[^{}]+\}) #label
|
(?: # comments
  (?:%.*?\n)+
  (?:%.*?(?:\n|$))
)
)
""", re.VERBOSE)


def transform_standard(math_string, config):
    def sanitize_whitespace(st, str_following=None):
        if st or (not st and str_following == ","):  # has whitespace or no whitespace but comma following
            return st
        else:
            return " "

    def repl_dot(matchobj):
        if matchobj.group('dot_type') == ".":
            dot_command = r"\dot"
        else:
            dot_command = r"\ddot"
        return "{before}{dot_command}{{{content}}}".format(before=matchobj.group('before'),
                                                           dot_command=dot_command,
                                                           content=matchobj.group('content'))

    def repl_cdot(matchobj):
        whitespace = sanitize_whitespace(matchobj.group('wspace'))
        return r"\cdot{whitespace}{after}".format(whitespace=whitespace, after=matchobj.group('after'))

    def repl_dots(matchobj):
        whitespace = sanitize_whitespace(matchobj.group('wspace'), str_following=matchobj.group('after'))
        return r"\dots{whitespace}{after}".format(whitespace=whitespace, after=matchobj.group('after'))

    trafo_count = dict()
    re_transformations = [("dot", re_dot_special, repl_dot),
                          ("dot", re_dot_normal, repl_dot),
                          ("frac", re_frac, r"{\g<nom>}{\g<denom>}"),
                          ("cdot", re_cdot, repl_cdot),
                          ("dots", re_dots, repl_dots)]

    for name, pattern, repl in re_transformations:
        if config[name] != "disabled":
            math_string, trafo_count[name] = re.subn(pattern, repl, math_string)
    return math_string


def transform_auto_align(math_string, config, env_type=None):
    if env_type in ["align", "align*"] and config["auto_align"] != "disabled":
        # add \\'s if missing
        if r"\\" not in math_string:
            content_parts = [line for line in math_string.split("\n") if line and not line.isspace()]
            math_string = "\n" + " \\\\\n".join(content_parts) + "\n"

        # if only one = per line and none are &='ed
        lines_split = math_string.split(r"\\")
        if all(line.count(r"=") == 1 and line.count(r"&=") == 0 for line in lines_split):
            line_split = [line.split(r"=") for line in lines_split]
            line_joined = [r"&=".join(l) for l in line_split]
            lines_joined = r"\\".join(line_joined)
            math_string = lines_joined

    return math_string


def transform_braket(math_string, config):
    if config["braket"] != "disabled":
        math_string = re.sub(re_braket_full, r"\\braket{\1}", math_string)
        math_string = re.sub(re_braket_ketbra, r"\\ket{\g<ket_c>}\g<between>\\bra{\g<bra_c>}", math_string)
        math_string = re.sub(re_braket_ket, r"\g<before>\\ket{\g<ket_c>}\g<after>", math_string)
        math_string = re.sub(re_braket_bra, r"\g<before>\\bra{\g<bra_c>}\g<after>", math_string)
    return math_string


def transform_simple(math_string, config):
    simple_transformations = [("arrow", r" -> ", r" \to "),
                              ("approx", r"~=", r"\approx"),
                              ("leq", r"<=", r"\leq"),
                              ("geq", r">=", r"\geq"),
                              ("ll", r"<<", r"\ll"),
                              ("gg", r">>", r"\gg"),
                              ("neq", r"!=", r"\neq")]
    single_backslash = r"\ "[0]
    for name, source, target in simple_transformations:
        if config[name] != "disabled":
            needs_whitespace = single_backslash in target and target[-1] != " "
            if needs_whitespace:
                if source + " " in math_string:
                    source += " "
                    target += " "
                else:
                    target += " "
            math_string = math_string.replace(source, target)
    return math_string


def transform_sub_superscript(math_string, config):
    if config["sub_superscript"] == "conservative":
        return re_sub_superscript_conservative.sub(r"\g<operator>\g<before>{\g<content>}\g<after>", math_string)
    elif config["sub_superscript"] == "aggressive":
        return re_sub_superscript_aggressive.sub(r"\g<operator>\g<before>{\g<content>}\g<after>", math_string)
    else:
        return math_string


def transform_math(math_string, config, env_type=None):
    """ the actual transformations with the math contents """

    math_string = transform_standard(math_string, config)
    math_string = transform_sub_superscript(math_string, config)
    math_string = transform_auto_align(math_string, config, env_type)
    math_string = transform_braket(math_string, config)
    math_string = transform_simple(math_string, config)
    return math_string


def next_config(config_string, config_passed, pos_start=0):
    """ returns tuple of string position where next config starts and the new
    config dict. position -1 if valid until end """

    re_config = re.compile(r"""
%\ pretex\ config\ (?P<key>\w+)
\ (?P<value>\w+)
""", re.VERBOSE)

    find = re_config.search(config_string, pos_start)
    if find:
        key, value = find.group("key"), find.group("value")

        # already using that config
        if config_passed[key] == value:
            return next_config(config_string, config_passed, find.end()+1)

        # set new config
        config_new = copy.deepcopy(config_passed)
        config_new[find.group("key")] = find.group("value")
        return find.start(), config_new

    else:
        return -1, config_passed


def replace_math_outer(math_outer_old, config):

    re_extract_math = re.compile(r"""
(?P<env_opening>
  \$\$|
  (?P<sd>\$)|
  \\\(|
  (?P<br_sq>\\\[)|
  \\begin\ *?{(?P<env_name>
    (?:
      equation|align|math|displaymath|eqnarray|gather|flalign|multiline|alignat
    )
    \*?)}
)
(?P<env_content>
  (?:\n|\\\$|.)+?
)
(?P<env_closing>
  (?(sd)\$|(
    (?(br_sq)\\\]|(
      \$\$|
      \\\]|
      \\\]|
      \\end\ *?{(?P=env_name)}
    ))
  ))
)
        """, re.VERBOSE)

    string_return = math_outer_old
    config_current = config
    pos_config_next, config_next = next_config(string_return, config_current, 0)

    pos_next_math = 0
    math_match = re_extract_math.search(string_return, pos_next_math)
    if math_match:
        pos_next_math = math_match.start()

    while math_match:
        while pos_next_math > pos_config_next and pos_config_next != -1:
            config_current = config_next
            pos_config_next, config_next = next_config(string_return, config_current, pos_config_next+1)

        repl = "{env_opening}{transformed}{env_closing}".format(
            env_opening=math_match.group("env_opening"),
            transformed=transform_math(math_match.group("env_content"), config_current,
                                       env_type=math_match.group("env_name")),
            env_closing=math_match.group("env_closing")
        )
        string_return = string_return[:math_match.start()] + repl + string_return[math_match.end():]

        math_match = re_extract_math.search(string_return, math_match.start()+len(repl))
        if math_match:
            pos_next_math = math_match.start()

    return string_return


def parse_cmd_arguments(config, parameters):
    """ returns a tuple of input-, output-filename and list of excluded commands. optional parameters default to None """

    def filename_sanitizer(filename):
        if "." not in filename:
            raise argparse.ArgumentTypeError("String '{s}' does not match required format".format(s=filename))
        return filename

    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", type=filename_sanitizer, help="pyth to file input")
    parser.add_argument("-o", "--output", dest="output_filename", type=filename_sanitizer, help="output file")
    parser.add_argument("-s", "--skip", dest="excluded_commands", action='append',
                        help="comma seperated list of transformations to exclude")
    args = parser.parse_args(parameters)

    # parse output filename
    if args.output_filename:
        output_filename = args.output_filename
    else:
        dot_position = args.input_filename.rfind(".")
        output_filename = args.input_filename[:dot_position] + "_t" + args.input_filename[dot_position:]

    # make sure output and input filename are not
    if args.input_filename == output_filename:
        raise ValueError("Output and input file are same. You're a crazy person! Abort!!!")

    # parse skip parameter into config
    if args.excluded_commands:
        for skip_cmd in args.excluded_commands:
            if skip_cmd not in config:
                raise argparse.ArgumentTypeError("Unknown transformation '{trafo}'".format(trafo=skip_cmd))
            else:
                config[skip_cmd] = "disabled"

    return args.input_filename, output_filename, config


def block_comments(math_string, config):
    math_string_parts = re.split(re_label_comments, math_string)
    for i in range(0, len(math_string_parts), 2):
        math_string_parts[i] = replace_math_outer(math_string_parts[i], config)
        math_string = "".join(math_string_parts)
    return math_string


def main():
    config = dict(arrow="enabled", approx="enabled", leq="enabled", geq="enabled", ll="enabled", gg="enabled",
                  neq="enabled", cdot="enabled", braket="enabled", dots="enabled", sub_superscript="conservative",
                  dot="disabled", frac="enabled", braket_style="small", auto_align="disabled")

    input_filename, output_filename, config = parse_cmd_arguments(config, parameters=sys.argv[1:])
    with io.open(input_filename, 'r', encoding='utf-8') as file_read:
        file_content = file_read.read()

    file_content = block_comments(file_content, config)

    with io.open(output_filename, 'w', encoding='utf-8') as file_out:
        file_out.write(file_content)


if __name__ == "__main__":
    main()  # pragma: no cover