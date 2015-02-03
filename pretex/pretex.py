# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import sys
import io
from docopt import docopt
from .Transformer import Transformer


def parse_cmd_arguments(config, parameters):
    """ returns a tuple of input-, output-filename and list of excluded
    commands. optional parameters default to None """

    parse_string = """
Usage:
  pretex <file> [--set <key>=<val>...] [--html] [-o <output_file>]

Options:
  --set <key>=<val> set settings like braket, cdot
  -h --help     Show this screen.
  --version     Show version.

Examples:
  pretex thesis.tex --set braket=disabled -o thesis_o.tex
"""
    args = docopt(parse_string, argv=parameters, version='preTeX 1.0.0')

    # parse config
    config_new = copy.deepcopy(config)
    if args["--set"]:
        for param in args["--set"]:
            setting, value = param.split("=")
            if setting not in config_new:
                raise ValueError("Unknown setting '{}'".format(setting))
            config_new[setting] = value
    config_new["html"] = {True: "enabled", False: "disabled"}[args["--html"]]

    # output filename
    output_filename = args["<output_file>"]
    if not output_filename:
        output_filename = "_t.".join(args["<file>"].split("."))

    # make sure output and input filename are not equal
    if args["<file>"] == output_filename:
        raise ValueError("Output and input file are same. You're a crazy person! Abort!!!")

    return (args["<file>"]), output_filename, config_new

def main():
    optimus_prime = Transformer()
    filename_in, filename_out, optimus_prime.config = parse_cmd_arguments(optimus_prime.config, parameters=sys.argv[1:])

    with io.open(filename_in,  'r', encoding='utf-8') as file_in, \
         io.open(filename_out, 'w', encoding='utf-8') as file_out:
        file_content_transformed = optimus_prime.get_transformed_str(file_in.read(), filename=filename_in)
        file_out.write(file_content_transformed)


if __name__ == "__main__":
    main()  # pragma: no cover
