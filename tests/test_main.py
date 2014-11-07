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
    # assert pretex.replace_math_outer(r"$ab.. f$") == r"$\ddot{ab} f$"
    # assert pretex.replace_math_outer(r"$f=f(x., x.., t)$") == r"$f=f(\dot{x}, \ddot{x}, t)$"


def test_re_int_sum():
    assert pretex.replace_math_outer(r"foo $\int_a^b-2 x^2$ bar!") == r"foo $\int_{a}^{b-2} x^2$ bar!"
    assert pretex.replace_math_outer(r"foo ${\oint_   a^b-2 x^2$ bar!") == r"foo ${\oint_{a}^{b-2} x^2$ bar!"


def test_frac():
    assert pretex.replace_math_outer(r"foo $\frac a+b c*d x$") == r"foo $\frac{a+b}{c*d} x$"
    assert pretex.replace_math_outer(r"foo $\frac{a+b}{c*d} x$") == r"foo $\frac{a+b}{c*d} x$"


def test_unicode():
    assert pretex.replace_math_outer(r"äüöé $äüöé\frac a+b c*d x$") == r"äüöé $äüöé\frac{a+b}{c*d} x$"


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
        pretex.parse_filenames([])
    with pytest.raises(SystemExit):
        pretex.parse_filenames(["test"])
    with pytest.raises(ValueError):
        pretex.parse_filenames(["test.tex", "-o", "test.tex"])
    assert pretex.parse_filenames(["test.tex", "-o", "test2.tex"]) == ("test.tex", "test2.tex")
    assert pretex.parse_filenames(["test.tex"]) == ("test.tex", "test_t.tex")