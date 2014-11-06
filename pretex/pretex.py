# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import sys
import argparse
import io

re_dot_special = re.compile(r"""
(?P<pre>^|\ |\(|\{)
(?P<content>
\\\w+?|             #\word.. b
\\vec\ \w|          #\vec p.. b
\\vec\{[^\$\{\}]+\} #\vec{abc}.. b. no nested {} because that's impossible in regex
)
(?P<type>\.|\.\.)
(?=$|\ |,|\)|\})
""", re.VERBOSE)

re_dot_normal = re.compile(r"""
(?P<pre>^|\ |\(|\{)
(?P<content>\w+?)
(?P<type>\.|\.\.)
(?=$|\ |,|\)|\})
""", re.VERBOSE)

re_int_sum = re.compile(r"""
(?<=\\)
(?P<symbol>int|iint|iiint|idotsint|oint|prod|sum)
\ *?_\ *?
([^\ {}]+?)
\ *\^\ *
([^\ {}]+)
""", re.VERBOSE)

re_frac = re.compile(r"""
(?<=\\frac)
\ +?
(?P<nom>[^\ \{\}]+?)
\ +?
(?P<denom>[^\ \{\}]+?)
(?=$|\ |,|\)|\})
""", re.VERBOSE)


def repl_dots(matchobj):
    if matchobj.group('type') == '..':
        begin = r"\ddot{"
    else:
        begin = r"\dot{"
    return "{before}{beginning}{content}}}".format(before=matchobj.group('pre'),
                                                   beginning=begin, content=matchobj.group('content'))


def repl_math(match):
    match_content = match.group(1)

    trafo_count = dict()
    transformations = {
        "dot_special": {"re": re_dot_special, "repl": repl_dots},
        "dot_normal": {"re": re_dot_normal, "repl": repl_dots},
        "int_sum": {"re": re_int_sum, "repl": r"\g<symbol>_{\2}^{\3}"},
        "frac": {"re": re_frac, "repl": r"{\g<nom>}{\g<denom>}"}
    }

    for name in ["dot_special", "dot_normal", "int_sum", "frac"]:
        # noinspection PyTypeChecker
        match_content, trafo_count[name] = re.subn(pattern=transformations[name]['re'],
                                                   repl=transformations[name]['repl'], string=match_content)
    # print("replacements in {s}: {count}".format(s=match_content, count=str(trafo_count)))
    return match_content


def wrap_in_math(match):
    return r"${new_expr}$".format(new_expr=repl_math(match))


def process_string(string_original):
    re_extract_math = re.compile(r"\$([^\$\n]+?)\$")
    string_transformed = re.sub(pattern=re_extract_math, repl=wrap_in_math, string=string_original)
    return string_transformed


def parse_filenames(parameters):
    def filename_sanitizer(filename):
        if "." not in filename:
            raise argparse.ArgumentTypeError("String '{s}' does not match required format".format(s=filename))
        return filename

    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", type=filename_sanitizer, help="pyth to file input")  # non-optional
    parser.add_argument("-o", "--output", dest="output_filename", type=filename_sanitizer, help="output file")  # optional
    args = parser.parse_args(parameters)

    if args.output_filename:
        output_filename = args.output_filename
    else:
        dot_position = args.input_filename.rfind(".")
        output_filename = args.input_filename[:dot_position] + "_t" + args.input_filename[dot_position:]

    if args.input_filename == output_filename:
        raise ValueError("Output and input file are same. You're a crazy person! Abort!!!")
    return args.input_filename, output_filename


def main():
    input_filename, output_filename = parse_filenames(parameters=sys.argv[1:])
    with io.open(input_filename, 'r', encoding='utf-8') as file_read:
        string_original = file_read.read()

    string_transformed = process_string(string_original)

    with io.open(output_filename, 'w', encoding='utf-8') as file_out:
        file_out.write(string_transformed)


if __name__ == "__main__":
    main()