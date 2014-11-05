# preTeX

preTeX is a small Python LaTeX preprocessor, designed to make LaTeX syntax more expressive and thereby the writing process easier. Since the most important part about LaTeX is math, and the other parts are mostly optional thanks to tools like Pandoc, the focus is on math environments. Example:

```latex
 in: The limit $\sum_i=0 ^ N+1 q_i.. p. \frac a+b x^2-1$
out: The limit $\sum_{i=0}^{N+1} \ddot{q_i} \dot{p} \frac{a+b}{x^2-1}$
```

This is not intended to replace LaTeX macros (newcommand etc), but rather enable things that are impossible or very tedious to do otherwise.

## Status/Roadmap
- Right now it only works in inline math, so not in `align` etc. Will definitely change
- Planning to select transformations either over a config file, or cmd parameters

New ideas are very welcome!

## Syntax
### dotting with `\dot`, `\ddot`
Makes writing time derivations much easier. Instead of writing `\dot{a}`, you can just write `a.`. Same for `\ddot`.  The expression must be limited on the left side by one of: " ", "(", "{" or the beginning of the math environment. Analog the trailing delimiter, plus ",". Examples:

```latex
foo x. bar % -> foo \dot{x} bar
foo q_i.. bar % -> foo \ddot{q_i} bar
foo \phi. bar % -> foo \dot{\phi} bar
foo \vec x. bar % -> foo \dot{\vec x} bar
foo \vec{abc}. bar % -> foo \dot{\vec{abc}} bar
```

The regular expression at the heart has been carefully crafted and tested, but when in doubt, seperate the inner components with spaces.

## Easier limits for `\sum`, `\int` and friends
Instead of `\int_{down}^{up}`, just leave the braces and delimit everything with spaces. So:
```latex
\sum _ i=1 ^ e^2+4 % -> \sum_{i=1}^{e^2+4}
```

## `\frac` without braces
replace the curly braces by spaces
```latex
foo \frac a+b c*d bar -> foo \frac{a+b}{c*d} bar
```
