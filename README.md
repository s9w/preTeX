[![Build Status](https://travis-ci.org/s9w/preTeX.svg?branch=master)](https://travis-ci.org/s9w/preTeX)
[![Coverage Status](https://coveralls.io/repos/s9w/preTeX/badge.png?branch=master)](https://coveralls.io/r/s9w/preTeX?branch=master) 

# preTeX
preTeX is a Python (2 and 3) LaTeX preprocessor designed to make LaTeX syntax more concise and thereby the writing process faster and the code more readable. It consists of a number of [Transformations](#transformations), which are largely RegEx-powered replacements. It's focused on math. Examples in text and gif:

```latex
 in: The limit $\sum_ i=0 ^ N+1        q_i..     p. \frac a+b  x^2-1 $
out: The limit $\sum_{i=0}^{N+1} \ddot{q_i} \dot{p} \frac{a+b}{x^2-1}$
```

![](https://raw.githubusercontent.com/s9w/preTeX/master/docs/sc.gif)

## Why / Motivation
The math syntax of LaTeX is powerful and a defacto standard even outside of LaTeX. But it's ~30 years old and has some curiosities that make it awkward to transfer certain expressions from your brain into TeX code. For example it's almost completely whitespace agnostic. So `\frac a+b 2` really is the same as `\frac{a}{+}b2` and not the probably expected `\frac{a+b}{2}`. There's a macro system which can alleviate some of it, but it's still limited to the slash-and-{}-heavy tex syntax.

## Safety
Most of the transformations do things that would be expected of a modern LaTeX and are mistakenly assumed by non-gurus, like translating `>>` to `\gg`. Others are more aggressive but simplify the syntax greatly. Only the safe ones are enabled by default and the entire process can be controlled by command line arguments.

preTeX is currently automatically tested on 8 randomly selected [arXiv](http://arxiv.org/) papers (323KB raw LaTeX) and makes sure they're untouched with default settings. Transformations are considered safe when they pass that test (among normal unit tests of course).

## Usage
To use, either install with `(sudo) pip install pretex` or simply put the `pretex.py` wherever you need it. The only mandatory argument is an input filename. You can also supply an output filename (default is `{original}_t.tex`) and change settings. Usage:

```
          pretex thesis.tex                       # for installed version
          
python pretex.py thesis.tex                       # for copied file
python pretex.py thesis.tex -o thesis_output.tex
python pretex.py thesis.tex --set braket=disabled --set sub_superscript=aggressive
```

There are no dependencies on other packages and is fully tested with Python 2.7 to 3.4. Works in any math mode I know of. That is: `$x$`, `$$x$$`, `\(x\)`, `\[x\]` for inline modes and in all of these math environments (starred and unstarred): `equation`, `align`, `math`, `displaymath`, `eqnarray`, `gather`, `flalign`, `multiline`, `alignat`.

Hint: This works well together with [Pandoc](https://github.com/jgm/pandoc/), which makes it possible to mix LaTeX with Markdown code.

## HTML output
This is experimental and mostly used for debbuging right now. Enable with `pretex --html ...`. Should write a `filename_viz.html` file in the sources directory that contains some highlighting  and hover information.

## Transformations

name  | input | output | default | notes
------------- | -----|--------|---|---
arrow  | `a -> b` | `a \to b` | enabled :white_check_mark: | [below](#arrow)
approx  | `a~=b` | `a\approx b` | enabled :white_check_mark:
leq  | `a<=b` | `a\leq b` | enabled :white_check_mark:
geq  | `a>=b` | `a\geq b` | enabled :white_check_mark:
ll  | `a<<b` | `a\ll b` | enabled :white_check_mark:
gg  | `a>>b` | `a\gg b` | enabled :white_check_mark:
neq  | `a != b` | `a \neq b` | enabled :white_check_mark:
cdot  | `a*b` | `a\cdot b` | enabled :white_check_mark: | [below](#cdot)
dots | `1, 2, ...` | `1, 2, \dots` | enabled :white_check_mark:
braket | `<a|b|c>` | `\braket{a|b|c}` | enabled :white_check_mark: | [below](#braket)
frac | `\frac a+b 2` | `\frac{a+b}{2}` | enabled :white_check_mark: | [below](#frac)
auto_align |  |  | enabled :white_check_mark: | [below](#auto_align)
substack | | | enabled :white_check_mark: | [below](#substack)
dot | `x..` | `\ddot{x}` | disabled :x: | [below](#dot)
sub_superscript | `e^a+b` | `e^{a+b}` | enabled :white_check_mark: | [below](#sub_superscript)
brackets | `(\frac 1 2)` | `\left(\frac 1 2\right)` | disabled :x: | [below](#brackets)

### arrow
Simple arrow expressions like `a -> b` get replaced by their LaTeX counterpart `a \to b`. Note the necessary whitespace around it.

There is an extension to this when it comes to writing text over arrows. The LaTeX way to do this is `5 \xrightarrow{+3} 8`. preTeX allows this to be written as `5 ->^{+3} 8`. Note that this command requires the `amsmath` package to be included.
 
Both transformations are enabled by default. To only allow the first one, use  `pretex --set arrow=simple`.

### auto_align
In an `align(*)` math environment when there is

1. 0 or 1 "=" on every line and
2. None of them is aligned by "&=" and
3. Two or more non-whitespace lines

Then they all get auto-aligned by replacing the `=` with `&=`. Also if there is no line separation with `\\`, it's added automatically for similar conditions. Only works on "sane" aligns, where there's no math on the same line as the begin and closing statements.

![](https://raw.githubusercontent.com/s9w/preTeX/master/docs/auto_align.gif)

### cdot
Works anywhere in math except for the case of `a^*` to prevent wrongful use in complex conjugation.

### braket
(This is about the [Bra-ket notation](http://en.wikipedia.org/wiki/Bra%E2%80%93ket_notation) from physics. Not to be confused with regular brackets)

A "natural" syntax for writing bras, kets, brakets and ketbras is supported. For `|ket>` and `<bra|` and `|ket><bra|`, there can't be any whitespace or curly braces in them and there have to be reasonable limits (space, braces, string start/end) before and after. That's because there is one tricky case where this could blow up: `{ x | x>0 }`

There's also `<a|b>` or `<a|b|c>` for which the rules are a bit more relaxed (whitespace allowed inside). They all get translated into their respective `\ket{}`, `\bra{}` and `\braket{}` commands. Those are not included in vanilla LaTeX, but you could either use the LaTeX package [braket](http://mirror.selfnet.de/tex-archive/macros/latex/contrib/braket/braket.pdf) which defines these, or define your own versions. Examples:

```latex
<a|b|c>      →  \braket{a|b|c}
|ket> <bra|  →  \ket{ket} \bra{bra}
|ke t>       →  |ke t>               % no whitespace inside!
```

### dot
Instead of writing `\dot{a}` for time derivations, just write `a.`. Same for `\ddot` and `a..`. Works for some more complex structures, too. Examples:

```latex
x.          →  \dot{x}
f(q_i..)    →  f(\ddot{q_i})
\phi.       →  \dot{\phi}
\vec x.     →  \dot{\vec x}
\vec{abc}.  →  \dot{\vec{abc}}
```

Rule of thumb: The dot expression works with surrounding spaces or at the beginning/end inside braces.

**Status:** There is one use case that breaks this: Using punctuation in math mode. If you end a perfectly valid math expression with a dot and actually want to make a dot, this can make an unwanted change. Example: `$a_i.$`. That's why it's disabled by default at the moment. This was just one case out of ~5000 lines of tex code though, working on it. Enable with `--set dot=enabled`.

### sub_superscript
For relaxing the LaTeX rules with sub- or superscripting things with `_` or `^`. In default mode, what's being raised/lowered has to be alphanumeric, + or -. In particular it's unsafe to use backslashes, equal signs or brackets. That's to make sure that super tight notation like `x^2+a_0` or ambiguous like `\tau_\alpha` stay untouched.

```latex
u_tt   →  u_{tt}
e^a+b  →  e^{a+b}
a_abc  →  a_{abc}
```

There is a more aggressive setting that allows even more relaxed expressions like

```latex
\tau_i=0        →  \tau{i=0}
a_i=0,j=0       →  a_{i=0,j=0}
a_\alpha,\beta  →  a_{\alpha,\beta}
```

That "aggressive" mode has to be enabled as a command line option (`--set sub_superscript aggressive`) and requires a space after the expression as a delimiter, even at the end of math mode! But allows anything inside except whitespace and curly brackets.

### frac
Instead of writing `\frac{}{}`, use spaces as delimiters.

```latex
\frac a+b c*d  →  \frac{a+b}{c*d}
\frac a+b 2    →  \frac{a+b}{2}
```

### substack
When typesetting a sum with two subscripted rows like:

![](https://raw.githubusercontent.com/s9w/preTeX/master/docs/big_sum.png)

LaTeX doesn't allow this with normal newlines and you need to invoke the `\substack` command from amsmath this way: `\sum_{\substack{i<m \\ j<n}}`. preTeX does this for you, so you can just write `\sum_{i<m \\ j<n}`. Enabled by default, needs `amsmath` package.

### brackets
Automatically changes ()'s to their `\left(` and `\right)` versions when they're not already like that. This can be typigraphically unwanted, so it's disabled by default. Activate with `pretex -set brackets=enabled ...`

## Roadmap / Ideas 
- braket-size would be neat to be able to set. Right now they default to the small versions (`\ket` etc). There are big versions (`\Ket`) but I have no clue what's a clever way to indicate their use in the code. Right now that's a config var, but that's global or too much effort for a per-use-case
- Verbose mode that reports changes
- auto-insert `\linebreak[0]` in inline math after punctuation and forced whitespace?