[![Build Status](https://travis-ci.org/s9w/preTeX.svg?branch=master)](https://travis-ci.org/s9w/preTeX)
[![Coverage Status](https://coveralls.io/repos/s9w/preTeX/badge.png?branch=master)](https://coveralls.io/r/s9w/preTeX?branch=master) 

# preTeX

preTeX is a small Python (2 and 3) LaTeX preprocessor, designed to make LaTeX syntax more expressive and thereby the writing process faster and the code more readable. It consists of a number of "transformations", which are really Regex-powered replacements. It's focused on math, since for the rest the is the most excellent Pandoc. Example:

```latex
 in: The limit $\sum_i=0 ^ N+1 q_i.. p. \frac a+b x^2-1$
out: The limit $\sum_{i=0}^{N+1} \ddot{q_i} \dot{p} \frac{a+b}{x^2-1}$
```

This is not intended to replace LaTeX macros (newcommand etc), but rather enable things that are impossible or very tedious to do otherwise. To use, supply an input file and an optional output file:

```
python pretex.py thesis.tex
python pretex.py thesis.tex -o thesis_output.tex
```

## Status/Roadmap
- ~~Right now it only works in inline math, so not in environments like `align` etc. Will definitely change~~. Done!
- Planning to select transformations either over a config file, or cmd parameters

New ideas are very welcome!

## Syntax
### Dotting with `\dot`, `\ddot`
Makes writing time derivations much easier. Instead of writing `\dot{a}`, you can just write `a.`. Same for `\ddot`. Examples:

```latex
foo x. bar -> foo \dot{x} bar
foo q_i.. bar -> foo \ddot{q_i} bar
foo \phi. bar -> foo \dot{\phi} bar
foo \vec x. bar -> foo \dot{\vec x} bar
foo \vec{abc}. bar -> foo \dot{\vec{abc}} bar
```

The regular expression at the heart of this has been carefully crafted and tested. But as usual with regex, explaining is a very difficult thing. Rules of thumb:
- Seperate the inner components with spaces
- Can start and end at reasonable delimiters (braces, spaces, beginnings/ends)

### Easier limits for `\sum`, `\int` and friends
Instead of `\int_{down}^{up}`, just leave the braces and delimit everything with spaces. So:
```latex
\sum _ i=1 ^ e^2+4 -> \sum_{i=1}^{e^2+4}
```

This works for `sum`, `prod`, `int`, `iint`, `iiint`, `idotsint`, `oint`.

### `\frac` without braces
Instead of writing \frac{}{}, you can just use (an arbitrary amout of) spaces
```latex
foo \frac a+b c*d bar -> foo \frac{a+b}{c*d} bar
```

### `\cdot` with `*`
instead of writing `a\cdot b`, just write `a*b`. Works anywhere in math except for the case of `a^*` to prevent wrongful use in complex conjugation

### `\dots` with `...`
instead of writing `a, b, \dots`, just write `a, b, ...`

## Limitations
Parsing LaTeX is difficult. Because of a lack of good Python LaTeX parsers, preTeX works with regular Expressions. But since LaTeX itself is not a regular language, this can always just be an approximation. Especially when using macros or escaped math delimiters in math mode, it's possible to outsmart preTeX.

 
