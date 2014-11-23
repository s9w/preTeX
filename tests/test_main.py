# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import argparse
import copy
import pytest
import json
import sys
import os
import io
from pretex import pretex
from pretex.Transformer import Transformer
from pretex.Transformer import get_inside_str


def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


@pytest.fixture(scope="module")
def trans(request):
    ttt = Transformer()
    return ttt


class TestClass(object):
    def test_get_file_parts_full(self, trans):
        test_string = get_inside_str(r'''
            header
            \begin{document}
            %comment1
            text
            %comment2a
            %comment2b
            $math$
            \end{document}
            after document
            ''')
        expected = ('header\n\\begin{document}',
                    '\n%comment1\ntext\n%comment2a\n%comment2b\n$math$\n',
                    '\\end{document}\nafter document')
        assert trans.get_file_parts(test_string) == expected


    def test_get_file_parts_bare(self, trans):
        test_string = get_inside_str(r'''
            %comment1
            text
            %comment2a
            %comment2b
            $math$
            ''')
        expected = ("", '%comment1\ntext\n%comment2a\n%comment2b\n$math$', "")
        assert trans.get_file_parts(test_string) == expected


    def test_get_pretextec_tree_inline(self, trans):
        test_str = get_inside_str(r'''
            text $x^2$ bar
            ''')
        result = trans.get_pretextec_tree(test_str)
        expected = [{'type': 'text', 'content': 'text $'},
                    {'type': 'math_env', 'pretexes': [], 'content': 'x^2'},
                    {'type': 'text', 'content': '$ bar'}]
        assert result == expected


    def test_get_pretextec_tree_env(self, trans):
        test_str = get_inside_str(r'''
            text
            \begin{align}
            a*b
            \end{align}
            ''')
        result = trans.get_pretextec_tree(test_str)
        expected = [{'content': 'text\n\\begin{align}', 'type': 'text'},
                    {'content': '\na\\cdot b\n', 'pretexes':
                        [{'start': 2, 'end': 8, 'type': 'cdot'}],
                     'type': 'math_env'},
                    {'content': '\\end{align}', 'type': 'text'}]
        assert result == expected


    def test_get_transformed_str_basic(self, trans):
        test_str = get_inside_str(r'''
            a\begin{document}
            text %comm 1
            \begin{align}
            a*b %comm 2
            \end{align}
            \end{document}b
            ''')
        test_str_expected = get_inside_str(r'''
            a\begin{document}
            text %comm 1
            \begin{align}
            a\cdot b %comm 2
            \end{align}
            \end{document}b
            ''')
        result = trans.get_transformed_str(test_str)
        assert result == test_str_expected


    def test_parse_filenames(self, trans):
        default_config = trans.get_default_config()
        with pytest.raises(SystemExit):
            pretex.parse_cmd_arguments(default_config, [])
        with pytest.raises(ValueError):
            pretex.parse_cmd_arguments(default_config, "same_filename.tex -o same_filename.tex".split())
        with pytest.raises(argparse.ArgumentTypeError):
            pretex.parse_cmd_arguments(default_config, "test.tex -s unknown_command=disabled".split())
        with pytest.raises(SystemExit):
            pretex.parse_cmd_arguments(default_config, "test.tex -s wrong_format".split())

        assert pretex.parse_cmd_arguments(default_config, "in.tex -o out.tex".split()) == (
            "in.tex", "out.tex", default_config, "")
        assert pretex.parse_cmd_arguments(default_config, ["in.tex"]) == ("in.tex", "in_t.tex", default_config, "")

        config_expected = copy.deepcopy(default_config)
        config_expected["cdot"] = "disabled"
        assert pretex.parse_cmd_arguments(default_config, "test.tex -s cdot=disabled".split()) == (
            "test.tex", "test_t.tex", config_expected, "")

        config_expected = copy.deepcopy(default_config)
        config_expected["cdot"] = "disabled"
        config_expected["geq"] = "disabled"
        assert pretex.parse_cmd_arguments(default_config, "in.tex --set cdot=disabled --set geq=disabled".split()) == (
            "in.tex", "in_t.tex", config_expected, "")

        config_expected = copy.deepcopy(default_config)
        config_expected["html"] = "enabled"
        assert pretex.parse_cmd_arguments(default_config, "in.tex --html".split()) == (
            "in.tex", "in_t.tex", config_expected, "")


    def test_interactive(self, monkeypatch, trans, capsys):
        monkeypatch.setattr(sys, 'argv', ["xx", "a ... b"])
        pretex.main()
        out, err = capsys.readouterr()
        assert out == "a \\dots  b\n"

        monkeypatch.setattr(sys, 'argv', ["xx", "a ... b", "--set", "dots=disabled"])
        pretex.main()
        out, err = capsys.readouterr()
        assert out == "a ... b\n"


    def test_re_sub_superscript(self, trans):
        trans.config["sub_superscript"] = "enabled"
        test_cases = [
            (r"a_abc", r"a_{abc}"),
            (r"a_ abc b", r"a_ {abc} b"),
            (r"e^a+b", r"e^{a+b}"),
            (r"\tau_1+\tau_2", ""),
            (r"\tau_\alpha", "")
        ]
        for test_input, expected_output in test_cases:
            output = trans.get_transformed_math(test_input, trans.config)
            assert output[0] == (expected_output or test_input)


    def test_re_sub_superscript_agg(self, trans):
        trans.config["sub_superscript"] = "aggressive"
        test_cases = [
            (r"a_abc", r"a_{abc}"),
            (r"a_ abc b", r"a_ {abc} b"),
            (r"e^a+b", r"e^{a+b}"),
            (r"\tau_1+\tau_2", ""),
            (r"\tau_\alpha", ""),
            (r"a_i=0,j=0 ", r"a_{i=0,j=0} "),
            (r"\int_n=1 ^42+x ", r"\int_{n=1} ^{42+x} ")
        ]
        for test_input, expected_output in test_cases:
            output = trans.get_transformed_math(test_input, trans.config)
            assert output[0] == (expected_output or test_input)


    def test_cdot(self, trans):
        trans.config["cdot"] = "enabled"
        test_cases = [
            (r"a*b", r"a\cdot b"),
            (r"a*b*c", r"a\cdot b\cdot c"),
            (r"a^*b", "")
        ]
        for test_input, expected_output in test_cases:
            assert trans.get_transformed_math(test_input, trans.config)[0] == (expected_output or test_input)


    def test_dots(self, trans):
        trans.config["dots"] = "enabled"
        test_cases = [
            (r"1,...,...b", r"1,\dots ,\dots b"),
            (r"a....b", r"a....b")]
        for test_input, expected_output in test_cases:
            output = trans.get_transformed_math(test_input, trans.config)
            assert output[0] == expected_output


    def test_frac(self, trans):
        trans.config["frac"] = "enabled"
        test_cases = [
            (r"\frac a+b c+d", r"\frac{a+b}{c+d}"),
            (r"\frac a+b 2", r"\frac{a+b}{2}"),
            (r"\frac {a+b 2", r"\frac {a+b 2"),
            (r"\frac aa bb \frac aa bb", r"\frac{aa}{bb} \frac{aa}{bb}")
        ]
        for test_input, expected_output in test_cases:
            assert trans.get_transformed_math(test_input, trans.config)[0] == expected_output


    def test_dot_normal(self, trans):
        trans.config["dot"] = "enabled"
        test_cases = [(r"a b. c", r"a \dot{b} c")]
        for test_input, expected_output in test_cases:
            assert trans.get_transformed_math(test_input, trans.config)[0] == expected_output


    def test_re_ddot_easy(self, trans):
        trans.config["dot"] = "enabled"
        testcases = [
            (r"$a \phi.. b$", r"$a \ddot{\phi} b$"),
            (r"b.f", r"b.f"),
            (r"b. f", r"\dot{b} f"),
            (r"b. f", r"\dot{b} f"),
            (r"ab.. f", r"\ddot{ab} f"),
            (r"f=f(x., x.., t)", r"f=f(\dot{x}, \ddot{x}, t)")
        ]
        for test_input, test_output in testcases:
            result = trans.get_transformed_math(test_input, trans.config)
            assert result[0] == test_output


    def test_re_ddot_compl(self, trans):
        trans.config["dot"] = "enabled"
        invalid_testcases = [r"$\phi..b$", r"$a\vec x..b$", r"$a\vec{abc}..b$"]
        for test_input in invalid_testcases:
            assert trans.get_transformed_math(test_input, trans.config)[0] == test_input

        testcases = [
            (r"a \phi.. b", r"a \ddot{\phi} b"),
            (r"a \phi..", r"a \ddot{\phi}"),
            (r"\varphi. ", r"\dot{\varphi} "),
            (r"a \vec x.. b", r"a \ddot{\vec x} b"),
            (r"{a \vec{abc}.)", r"{a \dot{\vec{abc}})"),
            (r"a q_i.. b", r"a \ddot{q_i} b")
        ]
        for test_input, expected_output in testcases:
            assert trans.get_transformed_math(test_input, trans.config)[0] == expected_output


    def test_braket(self, trans):
        trans.config["braket"] = "enabled"
        testcases = [
            (r"foo  bar <a|b|c>", r"foo  bar \braket{a|b|c}"),
            (r"foo  bar <a|b>", r"foo  bar \braket{a|b}"),
            (r"|ket>", r"\ket{ket}"),
            (r"|ket><bra|", r"\ket{ket}\bra{bra}"),
            (r"x|ket> <bra| x", r"x\ket{ket} \bra{bra} x"),
            (r"|ket>x", r"|ket>x"),
            (r"|ke t>", r"|ke t>"),
            (r"= { x | x>0 }", r"= { x | x>0 }")
        ]

        for test_input, test_output in testcases:
            result = trans.get_transformed_math(test_input, trans.config)
            assert result[0] == test_output


    def test_arrow(self, trans):
        testcases = [
            (r"a -> b", r"a \to b"),
            (r"a ->^{1+1} b", r"a \xrightarrow{1+1} b"),
        ]
        for test_input, test_output in testcases:
            result = trans.get_transformed_math(test_input, trans.config)
            assert result[0] == test_output

        trans.config["arrow"] = "conservative"
        testcases = [
            (r"a -> b", r"a \to b"),
            (r"a ->^{1+1} b", ""),
        ]
        for test_input, test_output in testcases:
            result = trans.get_transformed_math(test_input, trans.config)
            assert result[0] == test_output or test_input


    def test_substack(self, trans):
        testcases = [
            (r"\sum_{i<m \\ j<n}", r"\sum_{\substack{i<m \\ j<n}}"),
            (r"\sum_{\substack{i<m \\ j<n}}", r""),
        ]
        for test_input, test_output in testcases:
            result = trans.get_transformed_math(test_input, trans.config)
            assert result[0] == test_output or test_input


    def test_simple(self, trans):
        test_cases = [
            ("arrow", r"a -> b", r"a \to b"),
            ("arrow", r"a ->  b", r"a \to  b"),
            ("approx", r"a~=b", r"a\approx b"),
            ("approx", r"a~= b", r"a\approx  b"),
            ("approx", r"a~=  b", r"a\approx   b"),
            ("leq", r"a<=b", r"a\leq b"),
            ("geq", r"a>=b", r"a\geq b"),
            ("ll", r"a<<b", r"a\ll b"),
            ("gg", r"a>>b", r"a\gg b"),
            ("neq", r"a != b", r"a \neq  b")
        ]

        for name, test_input, test_output in test_cases:
            trans.config[name] = "enabled"
            result = trans.get_transformed_math(test_input, trans.config)
            assert result[0] == test_output


    def test_auto_align(self, trans):
        test_string_1 = r'''
            a = b \\
            x = y
            '''

        test_string_1_expected = r'''
            a &= b \\
            x &= y
            '''

        test_string_2 = r'''
            a = x = b \\
            x = y
            '''
        test_string_3 = r'''
            a = b \\
            x &= y
            '''

        test_string_4 = r'''
            a = b

            x = y
            '''

        test_string_4_expected = r'''
            a &= b \\

            x &= y
            '''

        trans.config["auto_align"] = "enabled"
        assert trans.get_transformed_math(test_string_1, "align")[0] == test_string_1_expected
        assert trans.get_transformed_math(test_string_2, "align")[0] == test_string_2
        assert trans.get_transformed_math(test_string_3, "align")[0] == test_string_3
        assert trans.get_transformed_math(test_string_4, "align")[0] == test_string_4_expected

        trans.config["auto_align"] = "disabled"
        assert trans.get_transformed_math(test_string_1, "align")[0] == test_string_1


    def test_skip(self, trans):
        invariant_inputs = [
            (r"$a.$", ["dot"]),
            (r"$a..$", ["dot"]),
            (r"foo ${\oint\limits_ a^b-2 x^2$", ["sub_superscript"]),
            (r"foo $\frac a+b c+d x$", ["frac"]),
            (r"foo $ bar a*b$", ["cdot"]),
            (r"foo $ bar a, b, ..., n$", ["dots"]),
            (r"foo $ bar <a|b|c>$", ["braket"]),
            (r"foo $ a. <a|b|c>$", ["braket", "dot"]),
            (r"u_tt", ["sub_superscript"])
        ]
        for test_input, exclude_cmds in invariant_inputs:
            for cmd in exclude_cmds:
                trans.config[cmd] = "disabled"
            assert trans.get_transformed_math(test_input, trans.config)[0] == test_input


    @pytest.fixture(scope="module")
    def mock_testfile(self, request):
        with io.open("test_simple.tex", 'w', encoding='utf-8') as file_out:
            file_out.write(r"$\frac aa bb$")

        def cleanup():
            silent_remove("test_simple.tex")
            silent_remove("test_simple_t.tex")

        request.addfinalizer(cleanup)


    def test_main_simple(self, monkeypatch, mock_testfile):
        monkeypatch.setattr(sys, 'argv', "xxx test_simple.tex".split())
        pretex.main()
        with io.open("test_simple_t.tex", 'r', encoding='utf-8') as file_read:
            test_file_content = file_read.read()
        assert test_file_content == r"$\frac{aa}{bb}$"


    def test_main_complex(self, monkeypatch):
        monkeypatch.setattr(sys, 'argv', "xxx tests/test_file.tex --html --set auto_align=enabled --set brackets=enabled".split())
        pretex.main()
        with io.open("tests/test_file_t.tex", 'r', encoding='utf-8') as file_read:
            test_file_content = file_read.read()
        with io.open("tests/test_file_expected.tex", 'r', encoding='utf-8') as file_read:
            test_expected_content = file_read.read()
        assert test_file_content == test_expected_content
        silent_remove("tests/test_file_t.tex")


    def test_arxiv(self, monkeypatch):
        arxiv_files = [
            # "arxiv_temp.tex",
            "arxiv_astro-ph.tex",
            "arxiv_hep-ex.tex",
            "arxiv_hep-th.tex",
            "arxiv_math-ph.tex",
            "arxiv_physics.tex",
            "arxiv_quant-ph.tex",
            "arxiv_math.tex"
        ]
        for filename in arxiv_files:
            input_path = "tests/" + filename

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
