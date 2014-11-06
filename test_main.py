# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
import sys
import os
import io
from pretex.pretex import process_string, parse_filenames, main


def test_re_ddot_compl():
    invalid_inputs = [r"$\phi..b$", r"$a\vec x..b$", r"$a\vec{abc}..b$"]
    for i in invalid_inputs:
        assert process_string(i) == i
    assert process_string(r"$a \phi.. b$") == r"$a \ddot{\phi} b$"
    assert process_string(r"$a \phi..$") == r"$a \ddot{\phi}$"
    assert process_string(r"$\varphi. $") == r"$\dot{\varphi} $"
    assert process_string(r"$a \vec x.. b$") == r"$a \ddot{\vec x} b$"
    assert process_string(r"${a \vec{abc}.)$") == r"${a \dot{\vec{abc}})$"
    assert process_string(r"$a q_i.. b$") == r"$a \ddot{q_i} b$"


def test_re_ddot_easy():
    assert process_string(r"$b. f$") == r"$\dot{b} f$"
    assert process_string(r"$ab.. f$") == r"$\ddot{ab} f$"
    assert process_string(r"$f=f(x., x.., t)$") == r"$f=f(\dot{x}, \ddot{x}, t)$"


def test_re_int_sum():
    assert process_string(r"foo $\int_a^b-2 x^2$ bar!") == r"foo $\int_{a}^{b-2} x^2$ bar!"
    assert process_string(r"foo ${\oint_   a^b-2 x^2$ bar!") == r"foo ${\oint_{a}^{b-2} x^2$ bar!"


def test_frac():
    assert process_string(r"foo $\frac a+b c*d x$") == r"foo $\frac{a+b}{c*d} x$"
    assert process_string(r"foo $\frac{a+b}{c*d} x$") == r"foo $\frac{a+b}{c*d} x$"


def test_unicode():
    assert process_string(r"äüöé $äüöé\frac a+b c*d x$") == r"äüöé $äüöé\frac{a+b}{c*d} x$"

@pytest.fixture(scope="module")
def mock_testfile(request):
    def silent_remove(filename):
        try:
            os.remove(filename)
        except OSError:
            pass
    with io.open("test.tex", 'w', encoding='utf-8') as file_out:
        file_out.write(r"$\frac a b$")
    def cleanup():
        print ("teardown smtp")
        silent_remove("test.tex")
        silent_remove("test_t.tex")
    request.addfinalizer(cleanup)

def test_main(monkeypatch, mock_testfile):
    monkeypatch.setattr(sys, 'argv', ['xxx', 'test.tex'])
    main()
    with io.open("test_t.tex", 'r', encoding='utf-8') as file_read:
        test_file_content = file_read.read()
    assert test_file_content == r"$\frac{a}{b}$"

    monkeypatch.setattr(sys, 'argv', ['xxx', 'testtex'])
    with pytest.raises(SystemExit):
        main()


def test_parse_filenames():
    with pytest.raises(SystemExit):
        parse_filenames([])
    with pytest.raises(SystemExit):
        parse_filenames(["test"])
    with pytest.raises(ValueError):
        parse_filenames(["test.tex", "-o", "test.tex"])
    assert parse_filenames(["test.tex", "-o", "test2.tex"]) == ("test.tex", "test2.tex")
    assert parse_filenames(["test.tex"]) == ("test.tex", "test_t.tex")