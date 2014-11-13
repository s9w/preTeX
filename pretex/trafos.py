# coding=utf-8
import re


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

def transform_rest(math_string, config):
    def sanitize_whitespace(whitespace, str_following=None):
        if whitespace or str_following == ",":  # has whitespace or no whitespace but comma following
            return whitespace
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
    if config["braket"] == "enabled":
        math_string = re.sub(re_braket_full, r"\\braket{\1}", math_string)
        math_string = re.sub(re_braket_ketbra, r"\\ket{\g<ket_c>}\g<between>\\bra{\g<bra_c>}", math_string)
        math_string = re.sub(re_braket_ket, r"\g<before>\\ket{\g<ket_c>}\g<after>", math_string)
        math_string = re.sub(re_braket_bra, r"\g<before>\\bra{\g<bra_c>}\g<after>", math_string)
    return math_string


def transform_replace(math_string, config):
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
            needs_whitespace = single_backslash in target and not target.endswith(" ")
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