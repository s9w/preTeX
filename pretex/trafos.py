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

re_sub_brackets = re.compile(r"""
(?<!(\\left|right))(?P<type>[()])
""", re.VERBOSE)

re_sub_substack = re.compile(r"""
_\ *?\{
(?P<a>[^{}]*?) \\\\
(?P<b>[^{}]*?) \}
""", re.VERBOSE)

re_sub_arrow = re.compile(r"""
\ ->\^\{(?P<top>[^{}].*?)\}
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
        ("dots", re_dots, r"\\dots "),
        ("substack", re_sub_substack, r"_{\\substack{\g<a>\\\\\g<b>}} "),
        ("brackets", re.compile(r"(?<!\\left)\("), r"\\left("),
        ("brackets", re.compile(r"(?<!\\right)\)"), r"\\right)"),

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
    if config["arrow"] == "enabled":
        re_transformations.append(("arrow", re_sub_arrow, r" \\xrightarrow{\g<top>}"))
    if config["sub_superscript"] == "enabled":
        re_transformations.append(("sub_superscript", re_sub_superscript, r"\g<operator>\g<before>{\g<content>}\g<after>"))
    elif config["sub_superscript"] == "aggressive":
        re_transformations.extend([
            ("sub_superscript", re_sub_superscript_agg, r"\g<operator>\g<before>{\g<content>}\g<after>"),
            ("sub_superscript", re_sub_superscript, r"\g<operator>\g<before>{\g<content>}\g<after>")
        ])

    for name, pattern, repl in re_transformations:
        if config[name] != "disabled":
            if isinstance(pattern, str):
                match_pos = math_string.find(pattern)
                while match_pos != -1:
                    trafos.append({"type": name, "start": match_pos, "end": match_pos+len(repl)})
                    math_string = math_string.replace(pattern, repl, 1)
                    match_pos = math_string.find(pattern)

            else:
                match = pattern.search(math_string)
                while match:
                    match_expanded = match.expand(repl)
                    trafos.append({"type": name, "start": match.start(), "end": match.start()+len(match_expanded)})
                    math_string = math_string[:match.start()] + match_expanded + math_string[match.end():]
                    match = pattern.search(math_string, match.end())

    return math_string, trafos


def transform_auto_align(math_string, config, env_type=None):
    """ Trims the empty lines at the beginning at end. There have to be >=2
    "real" lines. For the &0, There have to be none of those already, and 0
    or 1 equal sign on every line. For the \\'s, there have to be none already.
    Both are independent """

    def isempty(s):
        return s == "" or s.isspace()

    def slashLine(line):
        return line + r" \\" if not isempty(line) else ""

    trafos = []
    if env_type in ["align", "align*"] and config["auto_align"] != "disabled":
        lines = math_string.split("\n")
        i1 = next((i for i in range(len(lines)) if not isempty(lines[i])), None)
        i2 = next((i for i in range(len(lines) - 1, 0, -1) if not isempty(lines[i])), None)
        if i1 and i2:
            real_line_count = i2 - i1 + 1
            if real_line_count >= 2:
                if all(line.count("=") in [0, 1] and line.count("&=") == 0 for line in lines):
                    lines = [el.replace("=", "&=") for el in lines]
                    trafos = [{"type": "auto_align", "start": 0, "end": 1}]
                if r"\\" not in math_string:
                    lines[i1:i2] = [slashLine(line) for line in lines[i1:i2]]
                    trafos = [{"type": "auto_align", "start": 0, "end": 1}]
                math_string = "\n".join(lines)

    return math_string, trafos
