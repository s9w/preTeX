# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import argparse
import copy
import pytest
import sys
import os
import io
from pretex import pretex

config_default = pretex.get_default_config()


def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def test_re_ddot_compl():
    invalid_testcases = [r"$\phi..b$", r"$a\vec x..b$", r"$a\vec{abc}..b$"]
    for i in invalid_testcases:
        assert pretex.transform_math_env(i, config_default) == i

    valid_testcases = [(r"$a \phi.. b$", r"$a \ddot{\phi} b$"),
                       (r"$a \phi..$", r"$a \ddot{\phi}$"),
                       (r"$\varphi. $", r"$\dot{\varphi} $"),
                       (r"$a \vec x.. b$", r"$a \ddot{\vec x} b$"),
                       (r"${a \vec{abc}.)$", r"${a \dot{\vec{abc}})$"),
                       (r"$a q_i.. b$", r"$a \ddot{q_i} b$")]

    config = copy.deepcopy(config_default)
    config["dot"] = "enabled"
    for test_input, test_output in valid_testcases:
        assert pretex.transform_math_env(test_input, config) == test_output


def test_math_detection():
    valid_testcases = [(r"1$x -> y$b", r"1$x \to y$b"),
                       (r"2$x -> y\$x -> y$b", r"2$x \to y\$x \to y$b")]
    for test_input, test_output in valid_testcases:
        assert pretex.transform_math_env(test_input, config_default) == test_output


def test_re_ddot_easy():
    valid_testcases = [(r"$a \phi.. b$", r"$a \ddot{\phi} b$"),
                       (r"$b.f$", r"$b.f$"),
                       (r"$b. f$", r"$\dot{b} f$"),
                       (r"$b. f$", r"$\dot{b} f$"),
                       (r"$ab.. f$", r"$\ddot{ab} f$"),
                       (r"$f=f(x., x.., t)$", r"$f=f(\dot{x}, \ddot{x}, t)$")]

    config = copy.deepcopy(config_default)
    config["dot"] = "enabled"
    for test_input, test_output in valid_testcases:
        assert pretex.transform_math_env(test_input, config) == test_output


def test_re_sub_superscript():
    config = copy.deepcopy(config_default)
    config["sub_superscript"] = "disabled"
    valid_testcases = [(r"$a_b$", r"$a_b$"),
                       (r"$a_bc_d$", r"$a_bc_d$"),
                       (r"$a_ abc b$", r"$a_ abc b$")]
    for test_input, test_output in valid_testcases:
        assert pretex.transform_math_env(test_input, config) == test_output

    config = copy.deepcopy(config_default)
    config["sub_superscript"] = "conservative"
    valid_testcases = [(r"$a_abc$", r"$a_abc$"),
                       (r"$a_ abc b$", r"$a_ {abc} b$")]
    for test_input, test_output in valid_testcases:
        assert pretex.transform_math_env(test_input, config) == test_output

    config = copy.deepcopy(config_default)
    config["sub_superscript"] = "aggressive"
    valid_testcases = [(r"$a_abc$", r"$a_{abc}$"),
                       (r"$a_ abc b$", r"$a_ {abc} b$")]
    for test_input, test_output in valid_testcases:
        assert pretex.transform_math_env(test_input, config) == test_output


def test_frac():
    assert pretex.transform_math_env(r"foo $\frac a+b c+d x$", config_default) == r"foo $\frac{a+b}{c+d} x$"
    assert pretex.transform_math_env(r"foo $\frac   a+b   c+d   x$", config_default) == r"foo $\frac{a+b}{c+d}   x$"
    assert pretex.transform_math_env(r"foo $\frac{a+b}{c+d} x$", config_default) == r"foo $\frac{a+b}{c+d} x$"


def test_cdot():
    assert pretex.transform_math_env(r"foo $ bar a*b$", config_default) == r"foo $ bar a\cdot b$"
    assert pretex.transform_math_env(r"foo $ bar a* b$", config_default) == r"foo $ bar a\cdot b$"
    assert pretex.transform_math_env(r"foo $ bar a*  b$", config_default) == r"foo $ bar a\cdot  b$"
    assert pretex.transform_math_env(r"foo $ bar a^*$", config_default) == r"foo $ bar a^*$"


def test_dots():
    assert pretex.transform_math_env(r"foo $ bar a, b, ..., n$", config_default) == r"foo $ bar a, b, \dots, n$"
    assert pretex.transform_math_env(r"foo $ bar a, b, ... , n$", config_default) == r"foo $ bar a, b, \dots , n$"
    assert pretex.transform_math_env(r"foo $ bar a..., b,... , n$", config_default) == r"foo $ bar a\dots, b,\dots , n$"


def test_braket():
    valid_testcases = [(r"foo $ bar <a|b|c>$", r"foo $ bar \braket{a|b|c}$"),
                       (r"foo $ bar <a|b>$", r"foo $ bar \braket{a|b}$"),
                       (r"$|ket>$", r"$\ket{ket}$"),
                       (r"$|ket><bra|$", r"$\ket{ket}\bra{bra}$"),
                       (r"$x|ket> <bra| x$", r"$x\ket{ket} \bra{bra} x$"),
                       (r"$|ket>x$", r"$|ket>x$"),
                       (r"$|ke t>$", r"$|ke t>$"),
                       (r"$= { x | x>0 }$", r"$= { x | x>0 }$")]

    for test_input, test_output in valid_testcases:
        assert pretex.transform_math_env(test_input, config_default) == test_output


def test_simple():
    valid_testcases = [("arrow", r"$a -> b$", r"$a \to b$"),
                       ("arrow", r"$a ->  b$", r"$a \to  b$"),
                       ("approx", r"$a~=b$", r"$a\approx b$"),
                       ("approx", r"$a~= b$", r"$a\approx b$"),
                       ("approx", r"$a~=  b$", r"$a\approx  b$"),
                       ("leq", r"$a<=b$", r"$a\leq b$"),
                       ("geq", r"$a>=b$", r"$a\geq b$"),
                       ("ll", r"$a<<b$", r"$a\ll b$"),
                       ("gg", r"$a>>b$", r"$a\gg b$"),
                       ("neq", r"$a != b$", r"$a \neq b$")]

    for name, string_input, string_output in valid_testcases:
        assert pretex.transform_math_env(string_input, config_default) == string_output
        config = copy.deepcopy(config_default)
        config[name] = "disabled"
        assert pretex.transform_math_env(string_input, config) == string_input


def test_auto_align():
    test_string_1 = r"""
    \begin {align}
a = b \\
x = y
\end{align}
"""

    test_string_1_expected = r"""
    \begin {align}
a &= b \\
x &= y
\end{align}
"""

    test_string_2 = r"""
\begin {align}
a = x = b \\
x = y
\end{align}
"""
    test_string_3 = r"""
\begin {align}
a = b \\
x &= y
\end{align}
"""

    test_string_4 = r"""
\begin {align*}
a = b
x = y
\end{align*}
"""

    test_string_4_expected = r"""
\begin {align*}
a &= b \\
x &= y
\end{align*}
"""

    config = copy.deepcopy(config_default)
    config["auto_align"] = "enabled"

    assert pretex.transform_math_env(test_string_1, config) == test_string_1_expected
    assert pretex.transform_math_env(test_string_2, config) == test_string_2
    assert pretex.transform_math_env(test_string_3, config) == test_string_3
    assert pretex.transform_math_env(test_string_4, config) == test_string_4_expected

    config = copy.deepcopy(config_default)
    config["auto_align"] = "disabled"
    assert pretex.transform_math_env(test_string_1, config) == test_string_1


def test_skip():
    invariant_inputs = [(r"$a.$", ["dot"]),
                        (r"$a..$", ["dot"]),
                        (r"foo ${\oint\limits_ a^b-2 x^2$", ["sub_superscript"]),
                        (r"foo $\frac a+b c+d x$", ["frac"]),
                        (r"foo $ bar a*b$", ["cdot"]),
                        (r"foo $ bar a, b, ..., n$", ["dots"]),
                        (r"foo $ bar <a|b|c>$", ["braket"]),
                        (r"foo $ a. <a|b|c>$", ["braket", "dot"]),
                        (r"u_tt", ["sub_superscript"])]
    for invariant_input, exclude_cmds in invariant_inputs:
        config_test = copy.deepcopy(config_default)
        for cmd in exclude_cmds:
            config_test[cmd] = "disabled"
        assert pretex.transform_math_env(invariant_input, config_test) == invariant_input


def test_unicode():
    assert pretex.transform_math_env(r"äüöé $äüöé\frac a+b c+d x$", config_default) == r"äüöé $äüöé\frac{a+b}{c+d} x$"


@pytest.fixture(scope="module")
def mock_testfile(request):
    with io.open("test.tex", 'w', encoding='utf-8') as file_out:
        file_out.write(r"$\frac a b$")

    def cleanup():
        silent_remove("test.tex")
        silent_remove("test_t.tex")

    request.addfinalizer(cleanup)


def test_main_simple(monkeypatch, mock_testfile):
    monkeypatch.setattr(sys, 'argv', ['xxx', 'test.tex'])
    pretex.main()
    with io.open("test_t.tex", 'r', encoding='utf-8') as file_read:
        test_file_content = file_read.read()
    assert test_file_content == r"$\frac{a}{b}$"


def test_main_complex(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['xxx', 'tests/test_file.tex'])
    pretex.main()
    with io.open("tests/test_file_t.tex", 'r', encoding='utf-8') as file_read:
        test_file_content = file_read.read()
    with io.open("tests/test_file_expected.tex", 'r', encoding='utf-8') as file_read:
        test_expected_content = file_read.read()
    assert test_file_content == test_expected_content
    silent_remove("tests/test_file_t.tex")


def test_arxiv(monkeypatch):
    arxiv_files = ["arxiv_astro-ph.tex", "arxiv_hep-ex.tex", "arxiv_hep-th.tex", "arxiv_math-ph.tex",
                   "arxiv_physics.tex", "arxiv_quant-ph.tex", "arxiv_math.tex"]
    for filename in arxiv_files:
        input_path = "tests/"+filename

        dot_position = input_path.rfind(".")
        output_path = input_path[:dot_position] + "_t" + input_path[dot_position:]

        monkeypatch.setattr(sys, 'argv', ['xxx', input_path])
        pretex.main()
        with io.open(input_path, 'r', encoding='utf-8') as file_read:
            test_file_content = file_read.read()
        with io.open(output_path, 'r', encoding='utf-8') as file_read:
            test_expected_content = file_read.read()
        assert test_file_content == test_expected_content
        silent_remove(output_path)


def test_main_same_overwrite(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['xxx', 'testtex'])
    with pytest.raises(SystemExit):
        pretex.main()


def test_next_config():
    # no tags
    with io.open(r"tests/test_tags_none.tex", 'r', encoding='utf-8') as file_read:
        test_file_content = file_read.read()
    assert pretex.next_config(test_file_content, config_default) == (999999, config_default)

    # real test
    with io.open(r"tests/test_tags.tex", 'r', encoding='utf-8') as file_read:
        test_file_content = file_read.read()

    next_config_set = pretex.next_config(test_file_content, config_default)
    config_expected = config_default
    config_expected["braket"] = "disabled"
    assert next_config_set == (270, config_expected)

    test_config = next_config_set[1]
    next_config_set = pretex.next_config(test_file_content, test_config, next_config_set[0]+1)
    config_expected["braket"] = "enabled"
    assert next_config_set == (826, config_expected)

    test_config = next_config_set[1]
    next_config_set = pretex.next_config(test_file_content, test_config, next_config_set[0]+1)
    assert next_config_set == (999999, config_expected)


def test_parse_filenames():
    with pytest.raises(SystemExit):
        pretex.parse_cmd_arguments(config_default, [])
    with pytest.raises(SystemExit):
        pretex.parse_cmd_arguments(config_default, ["test_no_extension"])
    with pytest.raises(ValueError):
        pretex.parse_cmd_arguments(config_default, ["test.tex", "-o", "test.tex"])
    with pytest.raises(argparse.ArgumentTypeError):
        pretex.parse_cmd_arguments(config_default, ["test.tex", "-s", "unknown_command"])

    assert pretex.parse_cmd_arguments(config_default, ["in.tex", "-o", "out.tex"]) == ("in.tex", "out.tex", config_default)
    assert pretex.parse_cmd_arguments(config_default, ["in.tex"]) == ("in.tex", "in_t.tex", config_default)

    config_expected = config_default
    config_expected["cdot"] = "disabled"
    assert pretex.parse_cmd_arguments(config_default, ["test.tex", "-s", "cdot"]) == ("test.tex", "test_t.tex", config_expected)

    config_expected = config_default
    config_expected["geq"] = "disabled"
    config_expected["frac_compact"] = "disabled"
    assert pretex.parse_cmd_arguments(config_default, ["in.tex", "-s", "frac_compact", "--skip", "geq"]) == ("in.tex", "in_t.tex", config_expected)