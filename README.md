# lpp
A small python LaTeX preprocessor to keep you sane while writing LaTeX math. It allows you to write LaTeX math faster and in a more concise way. Typical example would be:

```latex
in:  The limit $\sum_i=0 ^ N+1 f_i q.. p.$
out: The limit $\sum_{i=0}^{N+1} f_i \ddot{q}\dot{p}$
```

All following examples only work in inline math mode!

## dotting with `\dot`, `\ddot`
Makes writing time derivations much easier. Instead of writing `$\dot{a}$`, you can just write `$a..$`. Same for .. and \ddot. To be safe there are certain conditions. Summary:

To be safe, use a space after `x..` Examples:
```latex
foo_c.. bar % -> foo_\ddot{c} bar
e^c.. bar -> e^\ddot{c} bar
foo\phi.. bar -> foo\ddot{\phi} bar
foo\vec x.. bar -> foo\ddot{x} bar
foo\vec{abc}.. bar -> foo\\ddot{abc} bar
```

For simple cases, you can omnit the space:
```latex
a..b % beginning of math. -> \ddot{a}b
foo x..b % space before. -> foo \ddot{x}b
e^{q..p}bar % beginning of {. -> e^{\ddot{q}p}bar
```

## Easier limits for `\sum` and `\int`
Instead of `\int_{down}^{up}`, just leave the braces and delimit everything with spaces. So:
```latex
\sum _ i=1 ^ e^2+4 -> \sum_{i=1}^{e^2+4}
```
