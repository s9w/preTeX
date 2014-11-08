[![Build Status](https://travis-ci.org/s9w/preTeX.svg?branch=master)](https://travis-ci.org/s9w/preTeX)
[![Coverage Status](https://coveralls.io/repos/s9w/preTeX/badge.png?branch=master)](https://coveralls.io/r/s9w/preTeX?branch=master) 

# preTeX

preTeX is a small Python (2 and 3) LaTeX preprocessor, designed to make LaTeX syntax more expressive and thereby the writing process faster and the code more readable. It consists of a number of "transformations", which are really Regex-powered replacements. It's focused on math, since for the rest the is the most excellent Pandoc. Example:

```latex
 in: The limit $\sum_i=0 ^ N+1 q_i.. p. \frac a+b x^2-1$
out: The limit $\sum_{i=0}^{N+1} \ddot{q_i} \dot{p} \frac{a+b}{x^2-1}$
```

This is not intended to replace LaTeX macros (newcommand etc), but rather enable things that are impossible or very tedious to do otherwise. To use, supply an input file and an optional output file. you can also exclude transformations.

```
python pretex.py thesis.tex
python pretex.py thesis.tex -o thesis_output.tex
python pretex.py thesis.tex --skip limits --skip cdot
```

## Transformations
Overview, but more below the table.

name  | input | output | notes
------------- | -----|--------|---
arrow  | `a -> b` | `a \to b`
cdot  | `a*b` | `a\cdot b` | Works anywhere in math except for the case of `a^*` to prevent wrongful use in complex conjugation
braket | `<a|b|c>` | `\braket{a|b|c}` | Does require the [braket](http://mirror.selfnet.de/tex-archive/macros/latex/contrib/braket/braket.pdf) package of course
dots | `1, 2, ...` | `1, 2, \dots`
dot | `x..` | `\ddot{x}` | see below for more info
limits | `\sum_i=1 ^ 1+1` | `\sum_{i=1}^{1+1}` | see below for more info
displaymath | `d$x^2$` | `$\displaymath x^2$` | see below for more info
frac | `\frac a+b c*d` | `\frac{a+b}{c*d}` | see below for more info

### auto_align
In an `align` math environment when there is
1. Only one "=" on every line and
2. None of them is aligned by "&="
Then they all get auto-aligned by replacing the `=` with `&=`

```
\begin{align}   ->    \begin{align}
  a = b \\               a &= b \\
  x = y                  x &= y
\end{align}            \end{align}
```

### dot
Makes writing time derivations much easier. Instead of writing `\dot{a}`, you can just write `a.`. Same for `\ddot`. Works for some more complex structures, too. Examples:

```latex
foo x. bar -> foo \dot{x} bar
foo q_i.. bar -> foo \ddot{q_i} bar
foo \phi. bar -> foo \dot{\phi} bar
foo \vec x. bar -> foo \dot{\vec x} bar
foo \vec{abc}. bar -> foo \dot{\vec{abc}} bar
```

The regular expression at the heart of this has been carefully crafted and tested. But as usual with regex, explaining is a very difficult thing. Rules of thumb:
- Separate the inner components with spaces
- Can start and end at reasonable delimiters (braces, spaces, beginnings/ends)

### limits
Instead of `\int_{down}^{up}`, just leave the braces and delimit everything with spaces. Works for `sum`, `prod`, `int`, `iint`, `iiint`, `idotsint`, `oint` - with or without a following `\limits`.
```latex
\sum _ i=1 ^ e^2+4 -> \sum_{i=1}^{e^2+4}
```

### Easy `\displaymath` switch
Instead of writing `$\displaymath x^2$`, just write `d$x^2$`. So a single d before inline math makes it set in displaymath. Note that this is technically the only transformation that works outside of math mode

### frac
Instead of writing `\frac{}{}`, you can just use spaces as delimiters
```latex
foo \frac a+b c*d bar -> foo \frac{a+b}{c*d} bar
```

