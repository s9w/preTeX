# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import sys
import argparse
import io
import re
from .trafos import transform_sub_superscript, transform_auto_align, transform_braket, transform_replace, \
    transform_rest

pattern_label_comments = re.compile(r"""
(
  (?:\\label\{[^{}]+\}) #label
|
  (?: # comments
    (?:%.*?\n)+
    (?:%.*?(?:\n|$))
  )
)
""", re.VERBOSE)


def transform_math_content(math_string, config, env_type=None):
    """ the actual transformations with the math contents """
    math_string = transform_sub_superscript(math_string, config)
    math_string = transform_auto_align(math_string, config, env_type)
    math_string = transform_braket(math_string, config)
    math_string = transform_replace(math_string, config)
    math_string = transform_rest(math_string, config)
    return math_string


def next_config(s, config_passed, pos_start=0):
    """ returns tuple of string position where next config starts and the new
    config dict. position -1 if valid until end """

    re_config = re.compile(r"""
%\ pretex\ config\ (?P<key>\w+)
\ (?P<value>\w+)
""", re.VERBOSE)

    next_config_match = re_config.search(s, pos_start)
    config = copy.deepcopy(config_passed)
    if next_config_match:
        key, value = next_config_match.groups()

        if config[key] == value:
            return next_config(s, config, next_config_match.end()+1)
        else:
            config[next_config_match.group("key")] = next_config_match.group("value")
            return next_config_match.start(), config
    else:
        return 999999, config


def transform_math_env(math_outer_old, config):

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

    env_content = math_outer_old
    config_current = copy.deepcopy(config)
    pos_config_next, config_next = next_config(env_content, config_current, pos_start=0)

    math_match = re_extract_math.search(env_content, 0)
    while math_match:
        while math_match.start() > pos_config_next:
            config_current = copy.deepcopy(config_next)
            pos_config_next, config_next = next_config(env_content, config_current, pos_config_next+1)

        repl = "{env_opening}{transformed}{env_closing}".format(
            env_opening=math_match.group("env_opening"),
            transformed=transform_math_content(math_match.group("env_content"), config_current,
                                               env_type=math_match.group("env_name")),
            env_closing=math_match.group("env_closing")
        )
        env_content = "".join([env_content[:math_match.start()], repl, env_content[math_match.end():]])
        math_match = re_extract_math.search(env_content, math_match.start()+len(repl))

    return env_content


def parse_cmd_arguments(config, parameters):
    """ returns a tuple of input-, output-filename and list of excluded
    commands. optional parameters default to None """

    def filename_sanitizer(filename):
        if "." not in filename:
            raise argparse.ArgumentTypeError("String '{s}' does not match required format".format(s=filename))
        return filename

    config_new = copy.deepcopy(config)

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
            if skip_cmd not in config_new:
                raise argparse.ArgumentTypeError("Unknown transformation '{trafo}'".format(trafo=skip_cmd))
            else:
                config_new[skip_cmd] = "disabled"

    return args.input_filename, output_filename, config_new


def transform_string(input_string, config):
    """ filters out comments, labels etc and continues transforming the rest """
    input_string_parts = re.split(pattern_label_comments, input_string)
    for i in range(0, len(input_string_parts), 2):
        input_string_parts[i] = transform_math_env(input_string_parts[i], config)
    input_string = "".join(input_string_parts)
    return input_string


def get_default_config():
    config = {key: "enabled" for key in
              ["arrow", "approx", "leq", "geq", "ll", "gg", "neq", "cdot", "braket", "dots", "frac"]}
    config.update({key: "disabled" for key in ["dot", "auto_align"]})
    config["sub_superscript"] = "conservative"
    config["braket_style"] = "small"
    return config


def main():
    config = get_default_config()
    input_filename, output_filename, config = parse_cmd_arguments(config, parameters=sys.argv[1:])
    with io.open(input_filename, 'r', encoding='utf-8') as file_read:
        file_content = file_read.read()

    file_content = transform_string(file_content, config)

    with io.open(output_filename, 'w', encoding='utf-8') as file_out:
        file_out.write(file_content)


if __name__ == "__main__":
    main()  # pragma: no cover