# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import sys
import argparse
import io

from .Transformer import Transformer


def parse_cmd_arguments(config, parameters):
    """ returns a tuple of input-, output-filename and list of excluded
    commands. optional parameters default to None """

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
    config_new = copy.deepcopy(config)
    for skip_cmd in args.excluded_commands or []:
        if skip_cmd not in config_new:
            raise argparse.ArgumentTypeError("Unknown transformation '{trafo}'".format(trafo=skip_cmd))
        config_new[skip_cmd] = "disabled"

    return args.input_filename, output_filename, config_new


def main():
    optimus_prime = Transformer()
    filename_in, filename_out, optimus_prime.config = parse_cmd_arguments(optimus_prime.config, parameters=sys.argv[1:])

    with io.open(filename_in, 'r', encoding='utf-8') as file_in, \
            io.open(filename_out, 'w', encoding='utf-8') as file_out:
        s_transformed = optimus_prime.get_transformed_str(file_in.read())
        file_out.write(s_transformed)


if __name__ == "__main__":
    main()  # pragma: no cover