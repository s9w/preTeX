[![Build Status](https://travis-ci.org/s9w/preTeX.svg?branch=master)](https://travis-ci.org/s9w/preTeX)
[![Coverage Status](https://coveralls.io/repos/s9w/preTeX/badge.png?branch=master)](https://coveralls.io/r/s9w/preTeX?branch=master) 

# preTeX

preTeX is a Python (2 and 3) LaTeX preprocessor designed to make LaTeX syntax more concise and thereby the writing process faster and the code more readable. It consists of a number of "transformations", which are really RegEx-powered replacements. It's focused on math. Examples in text and gif:

```latex
 in: The limit $\sum_i=0 ^ N+1 q_i.. p. \frac a+b x^2-1$
out: The limit $\sum_{i=0}^{N+1} \ddot{q_i} \dot{p} \frac{a+b}{x^2-1}$
```

![](https://raw.githubusercontent.com/s9w/preTeX/master/docs/sc.gif)

This is not intended to replace LaTeX macros (`\newcommand` etc), but rather enable things that are impossible or very tedious otherwise. To use, either install via `(sudo) pip install pretex` or simply put the `pretex.py` wherever you need it. The only mandatory argument is an input filename. You can also supply an output filename (default is `{original}_t.tex`) and exclude transformations. Usage:

```
pretex thesis.tex                                     # for installed version
python pretex.py thesis.tex                           # for copied file
python pretex.py thesis.tex -o thesis_output.tex
python pretex.py thesis.tex --skip limits --skip cdot
```

No dependencies, tested with Python 2.6, 2.7, 3.2, 3.3, 3.4

Works in any math mode I know of. That is: `$x$`, `$$x$$`, `\(x\)`, `\[x\]` for inline and in every of these math environments (starred and unstarred): `equation`, `align`, `math`, `displaymath`, `eqnarray`, `gather`, `flalign`, `multiline`, `alignat`.

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
cdot  | `a*b` | `a\cdot b` | Works anywhere in math except for the case of `a^*` to prevent wrongful use in complex conjugation
braket | `<a|b|c>` | `\braket{a|b|c}` | Does require the [braket](http://mirror.selfnet.de/tex-archive/macros/latex/contrib/braket/braket.pdf) package of course
dots | `1, 2, ...` | `1, 2, \dots`
dot | `x..` | `\ddot{x}` | see below for more info
limits | `\sum_i=1 ^ 1+1` | `\sum_{i=1}^{1+1}` | see below for more info
displaymath | `d$x^2$` | `$\displaymath x^2$` | see below for more info
frac | `\frac a+b c*d` | `\frac{a+b}{c*d}` | see below for more info
frac_tiny | `a+b // c*d` | `\frac{a+b}{c*d}`

### auto_align
In an `align` math environment when there is

1. Only one "=" on every line and
2. None of them is aligned by "&="
Then they all get auto-aligned by replacing the `=` with `&=`.

```
\begin{align}   ->    \begin{align}
  a = b \\               a &= b \\
  x = y                  x &= y
\end{align}            \end{align}
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

### limits
Instead of `\int_{down}^{up}`, just leave the braces and delimit everything with spaces. Works for `sum`, `prod`, `int`, `iint`, `iiint`, `idotsint`, `oint` - with or without a following `\limits`.
```latex
\sum _ i=1 ^ e^2+4 -> \sum_{i=1}^{e^2+4}
```

### Easy `\displaymath` switch
Instead of writing `$\displaymath x^2$`, just write `d$x^2$`. So a single d before inline math makes it set in displaymath. Note that this is technically the only transformation that works outside of math mode.

### frac
Instead of writing `\frac{}{}`, you can just use spaces as delimiters.
```latex
foo \frac a+b c*d bar -> foo \frac{a+b}{c*d} bar
```

