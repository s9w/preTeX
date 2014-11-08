# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
import sys
import os
import io
from pretex import pretex


def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def test_re_ddot_compl():
    invalid_inputs = [r"$\phi..b$", r"$a\vec x..b$", r"$a\vec{abc}..b$"]
    for i in invalid_inputs:
        assert pretex.replace_math_outer(i) == i
    assert pretex.replace_math_outer(r"$a \phi.. b$") == r"$a \ddot{\phi} b$"
    assert pretex.replace_math_outer(r"$a \phi..$") == r"$a \ddot{\phi}$"
    assert pretex.replace_math_outer(r"$\varphi. $") == r"$\dot{\varphi} $"
    assert pretex.replace_math_outer(r"$a \vec x.. b$") == r"$a \ddot{\vec x} b$"
    assert pretex.replace_math_outer(r"${a \vec{abc}.)$") == r"${a \dot{\vec{abc}})$"
    assert pretex.replace_math_outer(r"$a q_i.. b$") == r"$a \ddot{q_i} b$"


def test_re_ddot_easy():
    assert pretex.replace_math_outer(r"$b. f$") == r"$\dot{b} f$"
    assert pretex.replace_math_outer(r"$ab.. f$") == r"$\ddot{ab} f$"
    assert pretex.replace_math_outer(r"$f=f(x., x.., t)$") == r"$f=f(\dot{x}, \ddot{x}, t)$"


def test_re_int_sum():
    assert pretex.replace_math_outer(r"foo $\int_a^b-2 x^2$ bar!") == r"foo $\int_{a}^{b-2} x^2$ bar!"
    assert pretex.replace_math_outer(r"foo ${\oint_   a^b-2 x^2$ bar!") == r"foo ${\oint_{a}^{b-2} x^2$ bar!"
    assert pretex.replace_math_outer(r"${\int\limits_   a^b-2 x^2$ bar!") == r"${\int\limits_{a}^{b-2} x^2$ bar!"


def test_frac():
    assert pretex.replace_math_outer(r"foo $\frac a+b c+d x$") == r"foo $\frac{a+b}{c+d} x$"
    assert pretex.replace_math_outer(r"foo $\frac{a+b}{c+d} x$") == r"foo $\frac{a+b}{c+d} x$"


def test_cdot():
    assert pretex.replace_math_outer(r"foo $ bar a*b$") == r"foo $ bar a\cdot b$"
    assert pretex.replace_math_outer(r"foo $ bar a^*$") == r"foo $ bar a^*$"


def test_dots():
    assert pretex.replace_math_outer(r"foo $ bar a, b, ..., n$") == r"foo $ bar a, b, \dots , n$"
    assert pretex.replace_math_outer(r"foo $ bar a..., b, ..., n$") == r"foo $ bar a\dots , b, \dots , n$"


def test_braket():
    assert pretex.replace_math_outer(r"foo $ bar <a|b|c>$") == r"foo $ bar \braket{a|b|c}$"


def test_arrow():
    assert pretex.replace_math_outer(r"$a -> b$") == r"$a \to b$"


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
    assert pretex.replace_math_outer(test_string_1) == test_string_1_expected
    assert pretex.replace_math_outer(test_string_2) == test_string_2
    assert pretex.replace_math_outer(test_string_3) == test_string_3


def test_skip():
    invariant_inputs = [(r"$a.$", ["dot"]),
                        (r"$a..$", ["dot"]),
                        (r"foo ${\oint\limits_   a^b-2 x^2$ bar!", ["limits"]),
                        (r"foo $\frac a+b c+d x$", ["frac"]),
                        (r"foo $ bar a*b$", ["cdot"]),
                        (r"foo $ bar a, b, ..., n$", ["dots"]),
                        (r"foo $ bar <a|b|c>$", ["braket"]),
                        (r"foo $ a. <a|b|c>$", ["braket", "dot"])]
    for invariant_input, ex_cmd in invariant_inputs:
        assert pretex.replace_math_outer(invariant_input, excluded_commands=ex_cmd) == invariant_input


def test_unicode():
    assert pretex.replace_math_outer(r"äüöé $äüöé\frac a+b c+d x$") == r"äüöé $äüöé\frac{a+b}{c+d} x$"


@pytest.fixture(scope="module")
def mock_testfile(request):
    with io.open("test.tex", 'w', encoding='utf-8') as file_out:
        file_out.write(r"$\frac a b$")

    def cleanup():
        print ("teardown smtp")
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


def test_main_same_overwrite(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['xxx', 'testtex'])
    with pytest.raises(SystemExit):
        pretex.main()


def test_parse_filenames():
    with pytest.raises(SystemExit):
        pretex.parse_cmd_arguments([])
    with pytest.raises(SystemExit):
        pretex.parse_cmd_arguments(["test"])
    with pytest.raises(ValueError):
        pretex.parse_cmd_arguments(["test.tex", "-o", "test.tex"])
    assert pretex.parse_cmd_arguments(["test.tex", "-o", "test2.tex"]) == ("test.tex", "test2.tex", None)
    assert pretex.parse_cmd_arguments(["test.tex"]) == ("test.tex", "test_t.tex", None)
    assert pretex.parse_cmd_arguments(["test.tex", "-s", "a"]) == ("test.tex", "test_t.tex", ["a"])