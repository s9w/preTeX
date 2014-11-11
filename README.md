[![Build Status](https://travis-ci.org/s9w/preTeX.svg?branch=master)](https://travis-ci.org/s9w/preTeX)
[![Coverage Status](https://coveralls.io/repos/s9w/preTeX/badge.png?branch=master)](https://coveralls.io/r/s9w/preTeX?branch=master) 

# preTeX

preTeX is a Python (2 and 3) LaTeX preprocessor designed to make LaTeX syntax more concise and thereby the writing process faster and the code more readable. It consists of a number of "transformations", which are largely RegEx-powered replacements. It's focused on math. Examples in text and gif:

```latex
 in: The limit $\sum_ i=0 ^ N+1        q_i..     p. \frac a+b  x^2-1 $
out: The limit $\sum_{i=0}^{N+1} \ddot{q_i} \dot{p} \frac{a+b}{x^2-1}$
```

![](https://raw.githubusercontent.com/s9w/preTeX/master/docs/sc.gif)

This is not intended to replace LaTeX macros (`\newcommand` etc), but rather enable things that are impossible or very tedious otherwise. To use, either install with `(sudo) pip install pretex` or simply put the `pretex.py` wherever you need it. The only mandatory argument is an input filename. You can also supply an output filename (default is `{original}_t.tex`) and exclude transformations. Usage:

```
pretex thesis.tex                                     # for installed version
python pretex.py thesis.tex                           # for copied file
python pretex.py thesis.tex -o thesis_output.tex
python pretex.py thesis.tex --skip braket --skip cdot
```

No dependencies, tested with Python 2.6, 2.7, 3.2, 3.3, 3.4. Works in any math mode I know of. That is: `$x$`, `$$x$$`, `\(x\)`, `\[x\]` for inline and in every of these math environments (starred and unstarred): `equation`, `align`, `math`, `displaymath`, `eqnarray`, `gather`, `flalign`, `multiline`, `alignat`. You can still write escaped dollar signs in math, they won't mess things up.

## Transformations
Overview, but more below the table.

name  | input | output | notes
------------- | -----|--------|---
arrow  | `a -> b` | `a \to b`
approx  | `a~=b` | `a\approx b`
leq  | `a<=b` | `a\leq b`
geq  | `a>=b` | `a\geq b`
ll  | `a<<b` | `a\ll b`
gg  | `a>>b` | `a\gg b`
neq  | `a != b` | `a \neq b`
cdot  | `a*b` | `a\cdot b` | see below for more info
braket | `<a|b|c>` | `\braket{a|b|c}` | see below for more info
dots | `1, 2, ...` | `1, 2, \dots`
sub_superscript | `\int_n=1 ^42+x` | `\int_{n=1} ^{42+x}` | see below for more info
dot | `x..` | `\ddot{x}` | see below for more info
displaymath | `d$x^2$` | `$\displaymath x^2$` | see below for more info
frac | `\frac a+b c*d` | `\frac{a+b}{c*d}` | see below for more info
frac_compact | `a+b // c*d` | `\frac{a+b}{c*d}`


### auto_align
In an `align` math environment when there is

1. Only one "=" on every line and
2. None of them is aligned by "&="

Then they all get auto-aligned by replacing the `=` with `&=`. Also if there is no line separation with `\\`, it's added automatically.

![](https://raw.githubusercontent.com/s9w/preTeX/master/docs/auto_align.gif)

### cdot
Works anywhere in math except for the case of `a^*` to prevent wrongful use in complex conjugation.

### braket
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
foo x. bar         -> foo \dot{x} bar
f(q_i..)           -> f(\ddot{q_i})
foo \phi. bar      -> foo \dot{\phi} bar
foo \vec x. bar    -> foo \dot{\vec x} bar
foo \vec{abc}. bar -> foo \dot{\vec{abc}} bar
```

Rule of thumb: The dot expression works with surrounding spaces or at the beginning/end inside braces.

### sub_superscript
When sub- or superscripting things with `_` or `^` you can delimit the **contents** by spaces or other **reasonable delimiters** instead of framing them in `{}`.
 
- **Content** means any alphanumeric characters, +, -, *, =. Or a comma, but only if followed by an alphanumeric char
- **Reasonable delimiters** means between the `_`/ `^` and the content you can use nothing or any amount of whitespace. After the content can be either whitespace, end of math environment, newline or closing brackets

It preserves whitespace and only braces things that need them (two or more characters). Following examples demonstrate its use and also that its careful enough to not change ugly but correct latex code

```latex
u_tt             -> u_{tt}
u_ t             -> u_ t
\int_i=1 ^\infty -> \int_{i=1} ^\infty
f_a=4            -> f_{a=4}
\phi_a=1,b=2 b   -> \phi_{a=1,b=2} b 
x_1x_2x_3        % not touched
x_1,x_2,x_3      % not touched
x_1, f=5         % not touched
```

### displaymath
Instead of writing `$\displaymath \int_i^\infty$`, just write `d$\int_i^\infty$`. So a single d before inline math makes it set in displaymath. Note that this is technically the only transformation that works outside of math mode.

### frac
Instead of writing `\frac{}{}`, you can just use spaces as delimiters.

```latex
foo \frac a+b c*d bar -> foo \frac{a+b}{c*d} bar
```

