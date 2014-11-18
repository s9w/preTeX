# coding=utf-8
import re


re_dot_special = re.compile(r"""
(?P<before>^|\ |\n|\(|\{)
(?P<content>
\\\w+?|             #\word.. b
\\vec\ \w|          #\vec p.. b
\\vec\{[^\{\}]+\} #\vec{abc}.. b. no nested {} because that's impossible in regex
)
\.
(?=$|\ |\n|,|\)|\})
""", re.VERBOSE)

re_ddot_special = re.compile(r"""
(?P<before>^|\ |\n|\(|\{)
(?P<content>
\\\w+?|             #\word.. b
\\vec\ \w|          #\vec p.. b
\\vec\{[^\{\}]+\} #\vec{abc}.. b. no nested {} because that's impossible in regex
)
\.\.
(?=$|\ |\n|,|\)|\})
""", re.VERBOSE)

re_dot_normal = re.compile(r"""
(?P<before>^|\ |\n|\(|\{)
(?P<content>\w+?)
\.
(?=$|\ |\n|,|\)|\})
""", re.VERBOSE)

re_ddot_normal = re.compile(r"""
(?P<before>^|\ |\n|\(|\{)
(?P<content>\w+?)
\.\.
(?=$|\ |\n|,|\)|\})
""", re.VERBOSE)

re_frac = re.compile(r"""
(?P<frac>\\frac)
\ +
(?P<num>    # 2 or more chars
  [^\{\n]   # don't start with {
  [^\ \n]+
)
\ +
(?P<denom>  # denominator can be a single char
  [^\{\n]
  [^\ \n]*
)
""", re.VERBOSE)

re_cdot = re.compile(r"""
(?<!\^)               # no ^ before to save complex conjugation
\*
(?=[\ \w\\\(])
""", re.VERBOSE)

re_dots = re.compile(r"""
(?<!\.)           # no dot before
\.{3}             # ...
(?!\.)            # no dot after
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
    \|(?P<ket_c>[^\|\ {}<>\n]+)>
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

re_sub_superscript = re.compile(r"""
(?<![_\^].)
(?P<operator>[_\^]) # ^ or _
(?P<before> # optional whitespace before
  \ *?
)
(?P<content>
  [a-zA-Z0-9]
  [a-zA-Z0-9\+\*\-]+
)

(?P<after>
  $|\ |\n|\|
)
""", re.VERBOSE)

re_sub_superscript_agg = re.compile(r"""
(?P<operator>[_\^]) # ^ or _
(?P<before> # optional whitespace before
  \ *?
)
(?P<content>
  [^\ \{\}\n\^\_]{2,}
)
(?P<after>\ )
""", re.VERBOSE)


def transform_main(math_string, config):
    trafos = []
    re_transformations = [
        ("dot", re_ddot_special, r"\g<before>\\ddot{\g<content>}"),
        ("dot", re_dot_special, r"\g<before>\\dot{\g<content>}"),
        ("dot", re_ddot_normal, r"\g<before>\\ddot{\g<content>}"),
        ("dot", re_dot_normal, r"\g<before>\\dot{\g<content>}"),

        ("frac", re_frac, r"\\frac{\g<num>}{\g<denom>}"),
        ("cdot", re_cdot, r"\\cdot "),
        ("dots", re_dots, r"\dots "),

        ("braket", re_braket_full, r"\\braket{\1}"),
        ("braket", re_braket_ketbra, r"\\ket{\g<ket_c>}\g<between>\\bra{\g<bra_c>}"),
        ("braket", re_braket_ket, r"\g<before>\\ket{\g<ket_c>}\g<after>"),
        ("braket", re_braket_bra, r"\g<before>\\bra{\g<bra_c>}\g<after>"),

        # simple replacements using str.replace(), not regex
        ("arrow", r" -> ", r" \to "),
        ("approx", r"~=", r"\approx "),
        ("leq", r"<=", r"\leq "),
        ("geq", r">=", r"\geq "),
        ("ll", r"<<", r"\ll "),
        ("gg", r">>", r"\gg "),
        ("neq", r"!=", r"\neq ")
    ]
    if config["sub_superscript"] == "enabled":
        re_transformations.append(("sub_superscript", re_sub_superscript, r"\g<operator>\g<before>{\g<content>}\g<after>"))
    elif config["sub_superscript"] == "aggressive":
        re_transformations.append(("sub_superscript", re_sub_superscript_agg, r"\g<operator>\g<before>{\g<content>}\g<after>"))
        re_transformations.append(("sub_superscript", re_sub_superscript, r"\g<operator>\g<before>{\g<content>}\g<after>"))


    for name, pattern, repl in re_transformations:
        if config[name] != "disabled":
            if isinstance(pattern, re._pattern_type):
                match = pattern.search(math_string)
                while match:
                    match_expanded = match.expand(repl)
                    trafos.append({"type": name, "start": match.start(), "end": match.start()+len(match_expanded)})
                    math_string = math_string[:match.start()] + match_expanded + math_string[match.end():]
                    match = pattern.search(math_string, match.end())

            else:
                match_pos = math_string.find(pattern)
                while match_pos != -1:
                    trafos.append({"type": name, "start": match_pos, "end": match_pos+len(repl)})
                    math_string = math_string.replace(pattern, repl, 1)
                    match_pos = math_string.find(pattern)

    return math_string, trafos


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
