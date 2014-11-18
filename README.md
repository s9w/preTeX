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

preTeX is currently automatically tested on 8 randomly selected [arXiv](http://arxiv.org/) papers (323KB raw latex) and makes sure they're untouched with default settings. Transformations are considered safe when they pass that test (among normal unit tests of course).

## Usage
To use, either install with `(sudo) pip install pretex` or simply put the `pretex.py` wherever you need it. The only mandatory argument is an input filename. You can also supply an output filename (default is `{original}_t.tex`) and exclude transformations. Usage:

```
pretex thesis.tex                                     # for installed version
python pretex.py thesis.tex                           # for copied file
python pretex.py thesis.tex -o thesis_output.tex
python pretex.py thesis.tex --skip braket --skip cdot
```

The default configuration can be seen in the table below.

There are no dependencies on other packages and fully tested with Python 2.7, 3.2, 3.3, 3.4. Works in any math mode I know of. That is: `$x$`, `$$x$$`, `\(x\)`, `\[x\]` for inline and in every of these math environments (starred and unstarred): `equation`, `align`, `math`, `displaymath`, `eqnarray`, `gather`, `flalign`, `multiline`, `alignat`.

Hint: This works well together with Pandoc, which makes it possible to mix LaTeX with Markdown code. 

## Transformations
Overview, but more below the table.

name  | input | output | default | notes
------------- | -----|--------|---|---
arrow  | `a -> b` | `a \to b` | enabled :white_check_mark:
approx  | `a~=b` | `a\approx b` | enabled :white_check_mark:
leq  | `a<=b` | `a\leq b` | enabled :white_check_mark:
geq  | `a>=b` | `a\geq b` | enabled :white_check_mark:
ll  | `a<<b` | `a\ll b` | enabled :white_check_mark:
gg  | `a>>b` | `a\gg b` | enabled :white_check_mark:
neq  | `a != b` | `a \neq b` | enabled :white_check_mark:
cdot  | `a*b` | `a\cdot b` | enabled :white_check_mark: | see [below](#cdot) for more info
dots | `1, 2, ...` | `1, 2, \dots` | enabled :white_check_mark:
dot | `x..` | `\ddot{x}` | disabled :x: | see [below](#dot) for more info
braket | `<a|b|c>` | `\braket{a|b|c}` | enabled :white_check_mark: | see [below](#braket) for more info
sub_superscript | `\int_n=1^42+x` | `\int_{n=1}^{42+x}` | conservative | see [below](#sub_superscript) for more info
auto_align |  |  | disabled :x: | see below for more info
frac | `\frac a+b c*d` | `\frac{a+b}{c*d}` | enabled :white_check_mark: | see [below](#frac) for more info

### auto_align
In an `align(*)` math environment when there is

1. Only one "=" on every line and
2. None of them is aligned by "&="

Then they all get auto-aligned by replacing the `=` with `&=`. Also if there is no line separation with `\\`, it's added automatically.

![](https://raw.githubusercontent.com/s9w/preTeX/master/docs/auto_align.gif)

**Status:** disabled by default right now since I wanted to finish a big refactor

### cdot
Works anywhere in math except for the case of `a^*` to prevent wrongful use in complex conjugation.

### braket
(This is about the [Bra-ket notation](http://en.wikipedia.org/wiki/Bra%E2%80%93ket_notation) from physics. Not to be confused with regular brackets)

A "natural" syntax for writing bras, kets, brakets and ketbras is supported. For `|ket>` and `<bra|` and `|ket><bra|`, there can't be any whitespace or curly braces in them and there have to be reasonable limits (space, braces, string start/end) before and after. That's because there is one tricky case where this could blow up:

```latex
{ x | x>0 }
```

There's also `<a|b>` or `<a|b|c>` for which the rules are a bit more relaxed (whitespace allowed inside). They all get translated into their respective `\ket{}`, `\bra{}` and `\braket{}` commands. Those are not included in vanilla LaTeX, but you could either use the LaTeX package [braket](http://mirror.selfnet.de/tex-archive/macros/latex/contrib/braket/braket.pdf) which defines these, or define your own versions. Examples:

```latex
<a|b|c>     -> \braket{a|b|c}
|ket> <bra| -> \ket{ket} \bra{bra}
|ke t>      -> |ke t>               % no whitespace inside!
```

### dot
Makes writing time derivations much easier. Instead of writing `\dot{a}`, you can just write `a.`. Same for `\ddot`. Works for some more complex structures, too. Examples:

```latex
(?P<frac>\\frac)
\ +?
(?P<num>[^\ \{\}\n\\]+?)
\ +?
(?P<denom>[^\ \{\}\n\\]+?)
(?=$|\ |\n|,)
```

Rule of thumb: The dot expression works with surrounding spaces or at the beginning/end inside braces.

**Status:** There is one use case that breaks this: Using punctuation in math mode. If you end a perfectly valid math expression with a dot and actually want to make a dot, this can make an unwanted change. Example: `$a_i.$`. That's why it's disabled by default unfortunately. This was just one case out of ~5000 lines of tex code though. Working on it

### sub_superscript
This is for relaxing the LaTeX rules with sub- or superscripting things with `_` or `^`. There are two different modes for this (besides disabling): `conservative` and `aggressive`. A little infographic for reference:

![](https://raw.githubusercontent.com/s9w/preTeX/master/docs/sub_superscript.png)

**Conservative** means that there has to be whitespace before and after. The content can be any alphanumeric character plus any of +, -, *, = and commas.

**Aggressive** means the whitespace before is optional and after there has to one of a number of "reasonable" things, i.e. whitespace, end of string, ending braces or another operator.

All modes preserves whitespace and only brace things that need them (two or more characters). Following examples demonstrate its use and also that its careful enough to not change ugly but correct latex code

```latex
x_1,x_2,x_3         % not touched
x_1, f=5            % not touched
u_ tt bar        -> u_ {tt} bar % all modes
u_tt             -> u_{tt}      % this and all following only in aggressive!
\int_i=1 ^\infty -> \int_{i=1} ^\infty
f_a=4            -> f_{a=4}
\phi_a=1,b=2 b   -> \phi_{a=1,b=2} b 
```

**Status:** There are certain super tight expressions like ` \tau_1+\tau_2 ` that are tricky, that's why there are no plus or `=` signs allowed. Also things like `\tau_\alpha` forced me to deactivate the slashes. Which unfortunately reduced this to the simple case of alphanumeric strings.

In theory I think that's a solvable problem, but I doubt that the answer lies in a RegEx. Proper parsing could open up new ways or something clever. Having two different modes feels hacky and wrong.)

### frac
Instead of writing `\frac{}{}`, use spaces as delimiters.

```latex
foo \frac a+b c*d bar -> foo \frac{a+b}{c*d} bar
```

Problem: If allowing backslashes for valid things like greek letters, it's hard to separate those from another frac, which would blow up quite bad

## Roadmap / Ideas 
- Auto insert `\left` / `\right` before brakets etc? But it's sometimes unwanted. Maybe some kind of heuristic
- braket-size would be neat to be able to set. Right now they default to the small versions (`\ket` etc). There are big versions (`\Ket`) but I have no clue what's a clever way to indicate their use in the code. Right now that's a config var, but that's global or too much effort for a per-use-case
- Verbose mode that reports changes
- Working on experimental visualizer. Primarily for debugging, but could be used for more. Not currently documented