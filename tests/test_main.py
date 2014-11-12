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
    invalid_testcases = [r"$\phi..b$", r"$a\vec x..b$", r"$a\vec{abc}..b$"]
    for i in invalid_testcases:
        assert pretex.replace_math_outer(i) == i

    valid_testcases = [(r"$a \phi.. b$", r"$a \ddot{\phi} b$"),
                       (r"$a \phi..$", r"$a \ddot{\phi}$"),
                       (r"$\varphi. $", r"$\dot{\varphi} $"),
                       (r"$a \vec x.. b$", r"$a \ddot{\vec x} b$"),
                       (r"${a \vec{abc}.)$", r"${a \dot{\vec{abc}})$"),
                       (r"$a q_i.. b$", r"$a \ddot{q_i} b$")]
    for test_input, test_output in valid_testcases:
        assert pretex.replace_math_outer(test_input) == test_output


def test_math_detection():
    valid_testcases = [(r"1$x -> y$b", r"1$x \to y$b"),
                       (r"2$x -> y\$x -> y$b", r"2$x \to y\$x \to y$b")]
    for test_input, test_output in valid_testcases:
        assert pretex.replace_math_outer(test_input) == test_output


def test_re_ddot_easy():
    valid_testcases = [(r"$a \phi.. b$", r"$a \ddot{\phi} b$"),
                       (r"$b.f$", r"$b.f$"),
                       (r"$b. f$", r"$\dot{b} f$"),
                       (r"$b. f$", r"$\dot{b} f$"),
                       (r"$ab.. f$", r"$\ddot{ab} f$"),
                       (r"$f=f(x., x.., t)$", r"$f=f(\dot{x}, \ddot{x}, t)$")]
    for test_input, test_output in valid_testcases:
        assert pretex.replace_math_outer(test_input) == test_output


def test_re_sub_superscript():
    valid_testcases = [(r"foo $\int_a^b-2 x^2$ bar!", r"foo $\int_a^{b-2} x^2$ bar!"),
                       (r"foo ${\oint_ a^b-2 x^2$ bar!", r"foo ${\oint_ a^{b-2} x^2$ bar!"),
                       (r"${\int\limits_ a^b-2 x ^2$ bar!", r"${\int\limits_ a^{b-2} x ^2$ bar!"),
                       (r"$u_tt$", r"$u_{tt}$"),
                       (r"$u _ t$", r"$u _ t$"),
                       (r"$f_a=1$", r"$f_{a=1}$"),
                       (r"$a _ tt ^   a,b$", r"$a _ {tt} ^   {a,b}$")]
    for test_input, test_output in valid_testcases:
        assert pretex.replace_math_outer(test_input) == test_output


def test_frac():
    assert pretex.replace_math_outer(r"foo $\frac a+b c+d x$") == r"foo $\frac{a+b}{c+d} x$"
    assert pretex.replace_math_outer(r"foo $\frac   a+b   c+d   x$") == r"foo $\frac{a+b}{c+d}   x$"
    assert pretex.replace_math_outer(r"foo $\frac{a+b}{c+d} x$") == r"foo $\frac{a+b}{c+d} x$"


def test_frac_tiny():
    assert pretex.replace_math_outer(r"$foo aa//b+b bar$") == r"$foo \frac{aa}{b+b} bar$"
    assert pretex.replace_math_outer(r"$foo aa // b +b bar$") == r"$foo \frac{aa}{b} +b bar$"


def test_cdot():
    assert pretex.replace_math_outer(r"foo $ bar a*b$") == r"foo $ bar a\cdot b$"
    assert pretex.replace_math_outer(r"foo $ bar a* b$") == r"foo $ bar a\cdot b$"
    assert pretex.replace_math_outer(r"foo $ bar a*  b$") == r"foo $ bar a\cdot  b$"
    assert pretex.replace_math_outer(r"foo $ bar a^*$") == r"foo $ bar a^*$"


def test_dots():
    assert pretex.replace_math_outer(r"foo $ bar a, b, ..., n$") == r"foo $ bar a, b, \dots, n$"
    assert pretex.replace_math_outer(r"foo $ bar a, b, ... , n$") == r"foo $ bar a, b, \dots , n$"
    assert pretex.replace_math_outer(r"foo $ bar a..., b,... , n$") == r"foo $ bar a\dots, b,\dots , n$"


def test_braket():
    valid_testcases = [(r"foo $ bar <a|b|c>$", r"foo $ bar \braket{a|b|c}$", {}),
                       (r"foo $ bar <a|b>$", r"foo $ bar \braket{a|b}$", {}),
                       (r"$|ket>$", r"$\ket{ket}$", {}),
                       (r"$|ket><bra|$", r"$\ket{ket}\bra{bra}$", {}),
                       (r"$x|ket> <bra| x$", r"$x\ket{ket} \bra{bra} x$", {}),
                       (r"$|ket>x$", r"$|ket>x$", {}),
                       (r"$|ke t>$", r"$|ke t>$", {}),
                       (r"$= { x | x>0 }$", r"$= { x | x>0 }$", {}),
                       (r"$|ket><bra|$", r"$\Ket{ket}\Bra{bra}$", {"braket_style": "braket_expanding"})]

    for test_input, test_output, modes in valid_testcases:
        assert pretex.replace_math_outer(test_input, modes=modes) == test_output


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
    for name, old, new in valid_testcases:
        assert pretex.replace_math_outer(old) == new
        assert pretex.replace_math_outer(old, [name]) == old


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
    assert pretex.replace_math_outer(test_string_1, ["auto_align"]) == test_string_1
    assert pretex.replace_math_outer(test_string_1) == test_string_1_expected
    assert pretex.replace_math_outer(test_string_2) == test_string_2
    assert pretex.replace_math_outer(test_string_3) == test_string_3
    assert pretex.replace_math_outer(test_string_4) == test_string_4_expected


def test_skip():
    invariant_inputs = [(r"$a.$", ["dot"]),
                        (r"$a..$", ["dot"]),
                        (r"foo ${\oint\limits_   a^b-2 x^2$", ["sub_superscript"]),
                        (r"foo $\frac a+b c+d x$", ["frac"]),
                        (r"foo $ bar a*b$", ["cdot"]),
                        (r"foo $ bar a, b, ..., n$", ["dots"]),
                        (r"foo $ bar <a|b|c>$", ["braket"]),
                        (r"foo $ a. <a|b|c>$", ["braket", "dot"]),
                        (r"foo $a // b$", ["frac_compact"]),
                        (r"u_tt", ["sub_superscript"])]
    for invariant_input, exclude_cmd in invariant_inputs:
        assert pretex.replace_math_outer(invariant_input, exclude_cmd) == invariant_input

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
#
#
# def test_arxiv(monkeypatch):
#     monkeypatch.setattr(sys, 'argv', ['xxx', 'tests/arxiv_astro-ph.tex'])
#     pretex.main()
#     with io.open("tests/arxiv_astro-ph.tex", 'r', encoding='utf-8') as file_read:
#         test_file_content = file_read.read()
#     with io.open("tests/arxiv_astro-ph_t.tex", 'r', encoding='utf-8') as file_read:
#         test_expected_content = file_read.read()
#     assert test_file_content == test_expected_content
#
#
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