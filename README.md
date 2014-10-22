# lpp
A small python LaTeX preprocessor to keep you sane while writing LaTeX math. It allows you to write LaTeX math faster and in a more concise way. Typical example would be:

```latex
in:  The limit $\sum_i=0 ^ N+1 q_i.. p. \frac a+b x^2-1$
out: The limit $\sum_{i=0}^{N+1} \ddot{q_i} \dot{p} \frac{a+b}{x^2-1}$
```

All following examples only work in inline math mode!

## dotting with `\dot`, `\ddot`
Makes writing time derivations much easier. Instead of writing `$\dot{a}$`, you can just write `$a..$`. Same for `\ddot`. The expression must be limited on the left side by one of: " ", "(", "{" or the beginning of the math environment. Analog the trailing delimiter, plus ",". Examples:
```latex
a x. b % -> a \dot{x} b
a q_i.. % b -> a \ddot{q_i} b
L=L(f.., q., t) % -> L=L(\ddot{f}, \dot{q}, t)
```

Three common special cases which are processed before that:
```latex
\phi.. % -> \ddot{\phi}
\vec x.. % -> \ddot{\vec x}
\vec{abc}.. % -> \ddot{abc}
```

## Easier limits for `\sum` and `\int`
Instead of `\int_{down}^{up}`, just leave the braces and delimit everything with spaces. So:
```latex
\sum _ i=1 ^ e^2+4 % -> \sum_{i=1}^{e^2+4}
```

## `\frac` without braces
replace the curly braces by spaces
