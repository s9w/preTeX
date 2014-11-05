# import lpp
from lpp.lpp import *


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